from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import statistics

from .user_modeling import UserProfile, QuestionInteraction, PerformanceLevel

class AdaptationStrategy(Enum):
    CONSERVATIVE = "conservative"  # Slower adaptation
    MODERATE = "moderate"         # Balanced adaptation
    AGGRESSIVE = "aggressive"     # Faster adaptation

class ConfidenceLevel(Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class DifficultyAdjustment:
    old_difficulty: int
    new_difficulty: int
    confidence: ConfidenceLevel
    reasoning: List[str]
    evidence_score: float
    timestamp: datetime

@dataclass
class PerformanceWindow:
    interactions: List[QuestionInteraction]
    window_start: datetime
    window_end: datetime
    accuracy: float
    avg_time: float
    avg_attempts: float
    difficulty_distribution: Dict[int, int]

class DifficultyAdapter:
    def __init__(self, adaptation_strategy: AdaptationStrategy = AdaptationStrategy.MODERATE):
        self.adaptation_strategy = adaptation_strategy
        self.logger = logging.getLogger(__name__)
        
        # Configuration based on strategy
        self.config = self._get_strategy_config(adaptation_strategy)
        
        # Minimum interactions required for reliable adaptation
        self.min_interactions_for_adaptation = 5
        self.performance_window_size = 10  # Last N interactions to consider
        
    def _get_strategy_config(self, strategy: AdaptationStrategy) -> Dict[str, Any]:
        """Get configuration parameters based on adaptation strategy"""
        configs = {
            AdaptationStrategy.CONSERVATIVE: {
                'accuracy_threshold_up': 0.85,      # Higher threshold to increase difficulty
                'accuracy_threshold_down': 0.4,     # Lower threshold to decrease difficulty
                'time_factor_weight': 0.2,          # Lower weight for time performance
                'confidence_threshold': 0.8,        # Higher confidence required
                'max_difficulty_jump': 1,           # Maximum change per adaptation
                'adaptation_frequency': 15,         # Adapt every N interactions
                'stability_bonus': 0.2              # Bonus for consistent performance
            },
            AdaptationStrategy.MODERATE: {
                'accuracy_threshold_up': 0.75,
                'accuracy_threshold_down': 0.5,
                'time_factor_weight': 0.3,
                'confidence_threshold': 0.6,
                'max_difficulty_jump': 1,
                'adaptation_frequency': 10,
                'stability_bonus': 0.15
            },
            AdaptationStrategy.AGGRESSIVE: {
                'accuracy_threshold_up': 0.65,
                'accuracy_threshold_down': 0.6,
                'time_factor_weight': 0.4,
                'confidence_threshold': 0.4,
                'max_difficulty_jump': 2,
                'adaptation_frequency': 5,
                'stability_bonus': 0.1
            }
        }
        return configs[strategy]

    async def adapt_difficulty(
        self,
        user_profile: UserProfile,
        recent_interactions: List[QuestionInteraction],
        subject: Optional[str] = None
    ) -> Optional[DifficultyAdjustment]:
        """
        Adapt user's difficulty level based on recent performance
        """
        try:
            # Filter interactions by subject if specified
            if subject:
                filtered_interactions = [
                    i for i in recent_interactions if i.subject == subject
                ]
            else:
                filtered_interactions = recent_interactions
            
            # Check if we have enough data
            if len(filtered_interactions) < self.min_interactions_for_adaptation:
                self.logger.info(f"Insufficient interactions for adaptation: {len(filtered_interactions)}")
                return None
            
            # Analyze recent performance
            performance_window = self._create_performance_window(
                filtered_interactions[-self.performance_window_size:]
            )
            
            # Calculate adaptation metrics
            adaptation_metrics = await self._calculate_adaptation_metrics(
                performance_window, user_profile
            )
            
            # Determine if adaptation is needed
            adjustment = await self._determine_difficulty_adjustment(
                user_profile.preferred_difficulty,
                adaptation_metrics,
                performance_window
            )
            
            return adjustment
            
        except Exception as e:
            self.logger.error(f"Error in difficulty adaptation: {e}")
            return None

    def _create_performance_window(self, interactions: List[QuestionInteraction]) -> PerformanceWindow:
        """Create a performance analysis window from interactions"""
        if not interactions:
            return PerformanceWindow(
                interactions=[], window_start=datetime.now(), window_end=datetime.now(),
                accuracy=0.0, avg_time=0.0, avg_attempts=0.0, difficulty_distribution={}
            )
        
        # Calculate basic metrics
        correct_count = sum(1 for i in interactions if i.is_correct)
        accuracy = correct_count / len(interactions)
        avg_time = sum(i.time_taken for i in interactions) / len(interactions)
        avg_attempts = sum(i.attempts for i in interactions) / len(interactions)
        
        # Calculate difficulty distribution
        difficulty_dist = {}
        for interaction in interactions:
            diff = interaction.difficulty
            difficulty_dist[diff] = difficulty_dist.get(diff, 0) + 1
        
        return PerformanceWindow(
            interactions=interactions,
            window_start=interactions[0].timestamp,
            window_end=interactions[-1].timestamp,
            accuracy=accuracy,
            avg_time=avg_time,
            avg_attempts=avg_attempts,
            difficulty_distribution=difficulty_dist
        )

    async def _calculate_adaptation_metrics(
        self,
        performance_window: PerformanceWindow,
        user_profile: UserProfile
    ) -> Dict[str, float]:
        """Calculate metrics for difficulty adaptation decision"""
        metrics = {
            'accuracy_score': 0.0,
            'time_efficiency_score': 0.0,
            'attempt_efficiency_score': 0.0,
            'consistency_score': 0.0,
            'difficulty_appropriateness': 0.0,
            'confidence_level': 0.0,
            'overall_performance': 0.0
        }
        
        if not performance_window.interactions:
            return metrics
        
        # Accuracy score (normalized)
        metrics['accuracy_score'] = performance_window.accuracy
        
        # Time efficiency score
        # Optimal time range: 60-180 seconds per question
        optimal_time_min, optimal_time_max = 60, 180
        if optimal_time_min <= performance_window.avg_time <= optimal_time_max:
            metrics['time_efficiency_score'] = 1.0
        elif performance_window.avg_time < optimal_time_min:
            # Too fast might indicate guessing
            metrics['time_efficiency_score'] = 0.7
        else:
            # Too slow
            excess_time = performance_window.avg_time - optimal_time_max
            metrics['time_efficiency_score'] = max(0.2, 1.0 - (excess_time / 300))
        
        # Attempt efficiency score
        if performance_window.avg_attempts <= 1.2:
            metrics['attempt_efficiency_score'] = 1.0
        elif performance_window.avg_attempts <= 2.0:
            metrics['attempt_efficiency_score'] = 0.7
        else:
            metrics['attempt_efficiency_score'] = 0.4
        
        # Consistency score (based on variance in performance)
        accuracies = []
        window_size = 3
        interactions = performance_window.interactions
        
        for i in range(len(interactions) - window_size + 1):
            window_correct = sum(1 for j in range(i, i + window_size) 
                               if interactions[j].is_correct)
            window_accuracy = window_correct / window_size
            accuracies.append(window_accuracy)
        
        if len(accuracies) > 1:
            accuracy_variance = statistics.variance(accuracies)
            metrics['consistency_score'] = max(0, 1.0 - (accuracy_variance * 2))
        else:
            metrics['consistency_score'] = 0.5
        
        # Difficulty appropriateness
        current_diff = user_profile.preferred_difficulty
        diff_performance = {}
        
        for interaction in performance_window.interactions:
            diff = interaction.difficulty
            if diff not in diff_performance:
                diff_performance[diff] = {'correct': 0, 'total': 0}
            diff_performance[diff]['total'] += 1
            if interaction.is_correct:
                diff_performance[diff]['correct'] += 1
        
        # Check performance at current difficulty
        if current_diff in diff_performance and diff_performance[current_diff]['total'] >= 3:
            current_diff_accuracy = (diff_performance[current_diff]['correct'] / 
                                   diff_performance[current_diff]['total'])
            # Optimal accuracy range: 60-80%
            if 0.6 <= current_diff_accuracy <= 0.8:
                metrics['difficulty_appropriateness'] = 1.0
            elif current_diff_accuracy > 0.8:
                metrics['difficulty_appropriateness'] = 0.6  # Too easy
            else:
                metrics['difficulty_appropriateness'] = 0.4  # Too hard
        else:
            metrics['difficulty_appropriateness'] = 0.5
        
        # Confidence level based on data quality
        data_quality_factors = [
            min(1.0, len(performance_window.interactions) / 10),  # Sample size
            metrics['consistency_score'],  # Performance consistency
            min(1.0, len(diff_performance) / 2),  # Difficulty variety
        ]
        metrics['confidence_level'] = sum(data_quality_factors) / len(data_quality_factors)
        
        # Overall performance score
        weights = {
            'accuracy_score': 0.4,
            'time_efficiency_score': self.config['time_factor_weight'],
            'attempt_efficiency_score': 0.2,
            'consistency_score': 0.1,
            'difficulty_appropriateness': 0.2
        }
        
        metrics['overall_performance'] = sum(
            metrics[key] * weight for key, weight in weights.items()
        )
        
        return metrics

    async def _determine_difficulty_adjustment(
        self,
        current_difficulty: int,
        metrics: Dict[str, float],
        performance_window: PerformanceWindow
    ) -> Optional[DifficultyAdjustment]:
        """Determine if and how to adjust difficulty"""
        
        reasoning = []
        adjustment_direction = 0
        confidence = ConfidenceLevel.LOW
        
        # Check if confidence threshold is met
        if metrics['confidence_level'] < self.config['confidence_threshold']:
            self.logger.info(f"Confidence too low for adaptation: {metrics['confidence_level']}")
            return None
        
        # Determine confidence level
        if metrics['confidence_level'] >= 0.8:
            confidence = ConfidenceLevel.VERY_HIGH
        elif metrics['confidence_level'] >= 0.6:
            confidence = ConfidenceLevel.HIGH
        elif metrics['confidence_level'] >= 0.4:
            confidence = ConfidenceLevel.MEDIUM
        else:
            confidence = ConfidenceLevel.LOW
        
        # Decision logic for increasing difficulty
        should_increase = (
            metrics['accuracy_score'] >= self.config['accuracy_threshold_up'] and
            metrics['time_efficiency_score'] >= 0.7 and
            metrics['attempt_efficiency_score'] >= 0.8
        )
        
        if should_increase:
            adjustment_direction = 1
            reasoning.append(f"High accuracy ({metrics['accuracy_score']:.2f}) indicates readiness for harder questions")
            reasoning.append(f"Good time efficiency ({metrics['time_efficiency_score']:.2f})")
            reasoning.append(f"Low attempt count ({metrics['attempt_efficiency_score']:.2f})")
        
        # Decision logic for decreasing difficulty
        should_decrease = (
            metrics['accuracy_score'] <= self.config['accuracy_threshold_down'] or
            (metrics['time_efficiency_score'] <= 0.3 and metrics['accuracy_score'] <= 0.6) or
            metrics['attempt_efficiency_score'] <= 0.4
        )
        
        if should_decrease and not should_increase:
            adjustment_direction = -1
            reasoning.append(f"Low accuracy ({metrics['accuracy_score']:.2f}) indicates questions are too difficult")
            
            if metrics['time_efficiency_score'] <= 0.3:
                reasoning.append(f"Taking too long per question ({performance_window.avg_time:.1f}s)")
            
            if metrics['attempt_efficiency_score'] <= 0.4:
                reasoning.append(f"Too many attempts per question ({performance_window.avg_attempts:.1f})")
        
        # Apply stability bonus for consistent performance
        if metrics['consistency_score'] >= 0.7:
            reasoning.append("Consistent performance pattern observed")
            # Reduce adjustment magnitude for stable performance
            if abs(adjustment_direction) > 0:
                stability_factor = 1.0 + self.config['stability_bonus']
                # This could influence the confidence or adjustment size
        
        # No adjustment needed
        if adjustment_direction == 0:
            return None
        
        # Calculate new difficulty
        max_jump = self.config['max_difficulty_jump']
        difficulty_change = max(-max_jump, min(max_jump, adjustment_direction))
        new_difficulty = max(1, min(4, current_difficulty + difficulty_change))
        
        # Don't adjust if already at boundary
        if new_difficulty == current_difficulty:
            return None
        
        return DifficultyAdjustment(
            old_difficulty=current_difficulty,
            new_difficulty=new_difficulty,
            confidence=confidence,
            reasoning=reasoning,
            evidence_score=metrics['overall_performance'],
            timestamp=datetime.now()
        )

    async def predict_performance_at_difficulty(
        self,
        user_profile: UserProfile,
        target_difficulty: int,
        recent_interactions: List[QuestionInteraction],
        subject: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Predict how user would perform at a different difficulty level
        """
        try:
            # Filter interactions by subject if specified
            if subject:
                filtered_interactions = [
                    i for i in recent_interactions if i.subject == subject
                ]
            else:
                filtered_interactions = recent_interactions
            
            if len(filtered_interactions) < 3:
                return {
                    'predicted_accuracy': 0.5,
                    'predicted_time': 120.0,
                    'confidence': 0.3
                }
            
            # Analyze performance by difficulty level
            difficulty_performance = {}
            for interaction in filtered_interactions:
                diff = interaction.difficulty
                if diff not in difficulty_performance:
                    difficulty_performance[diff] = {
                        'accuracies': [],
                        'times': [],
                        'attempts': []
                    }
                
                difficulty_performance[diff]['accuracies'].append(1 if interaction.is_correct else 0)
                difficulty_performance[diff]['times'].append(interaction.time_taken)
                difficulty_performance[diff]['attempts'].append(interaction.attempts)
            
            # Calculate performance trend
            if len(difficulty_performance) >= 2:
                # Use linear interpolation/extrapolation
                difficulties = sorted(difficulty_performance.keys())
                accuracies = []
                times = []
                
                for diff in difficulties:
                    perf = difficulty_performance[diff]
                    accuracies.append(statistics.mean(perf['accuracies']))
                    times.append(statistics.mean(perf['times']))
                
                # Simple linear prediction
                predicted_accuracy = self._linear_predict(difficulties, accuracies, target_difficulty)
                predicted_time = self._linear_predict(difficulties, times, target_difficulty)
                
                # Confidence based on data quality
                total_interactions = sum(len(perf['accuracies']) for perf in difficulty_performance.values())
                confidence = min(1.0, total_interactions / 15)
                
            else:
                # Single difficulty level - use baseline adjustments
                base_diff = list(difficulty_performance.keys())[0]
                base_perf = difficulty_performance[base_diff]
                
                base_accuracy = statistics.mean(base_perf['accuracies'])
                base_time = statistics.mean(base_perf['times'])
                
                # Apply difficulty adjustment factors
                difficulty_delta = target_difficulty - base_diff
                
                # Assume 15% accuracy drop per difficulty level increase
                accuracy_adjustment = -0.15 * difficulty_delta
                predicted_accuracy = max(0.1, min(0.95, base_accuracy + accuracy_adjustment))
                
                # Assume 30% time increase per difficulty level increase
                time_adjustment = 0.3 * difficulty_delta
                predicted_time = max(30, base_time * (1 + time_adjustment))
                
                confidence = min(0.6, len(base_perf['accuracies']) / 10)
            
            return {
                'predicted_accuracy': max(0.1, min(0.95, predicted_accuracy)),
                'predicted_time': max(30.0, min(600.0, predicted_time)),
                'confidence': confidence
            }
            
        except Exception as e:
            self.logger.error(f"Error predicting performance at difficulty: {e}")
            return {
                'predicted_accuracy': 0.5,
                'predicted_time': 120.0,
                'confidence': 0.3
            }

    def _linear_predict(self, x_values: List[float], y_values: List[float], target_x: float) -> float:
        """Simple linear prediction/extrapolation"""
        if len(x_values) != len(y_values) or len(x_values) < 2:
            return y_values[0] if y_values else 0.0
        
        # Calculate slope and intercept
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        # Avoid division by zero
        denominator = n * sum_x2 - sum_x * sum_x
        if abs(denominator) < 1e-10:
            return statistics.mean(y_values)
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n
        
        return slope * target_x + intercept

    async def get_optimal_difficulty_range(
        self,
        user_profile: UserProfile,
        recent_interactions: List[QuestionInteraction],
        subject: Optional[str] = None
    ) -> Tuple[int, int]:
        """
        Get the optimal difficulty range for the user
        """
        try:
            current_difficulty = user_profile.preferred_difficulty
            
            # Predict performance at adjacent difficulty levels
            predictions = {}
            for diff in range(max(1, current_difficulty - 1), min(5, current_difficulty + 2)):
                predictions[diff] = await self.predict_performance_at_difficulty(
                    user_profile, diff, recent_interactions, subject
                )
            
            # Find optimal range (accuracy between 60-80%)
            optimal_difficulties = []
            for diff, pred in predictions.items():
                if 0.6 <= pred['predicted_accuracy'] <= 0.8:
                    optimal_difficulties.append(diff)
            
            if optimal_difficulties:
                return (min(optimal_difficulties), max(optimal_difficulties))
            else:
                # Fallback to current difficulty ± 1
                return (max(1, current_difficulty - 1), min(4, current_difficulty + 1))
            
        except Exception as e:
            self.logger.error(f"Error calculating optimal difficulty range: {e}")
            current = user_profile.preferred_difficulty
            return (max(1, current - 1), min(4, current + 1))

    async def should_adapt_now(
        self,
        user_profile: UserProfile,
        recent_interactions: List[QuestionInteraction],
        last_adaptation: Optional[datetime] = None
    ) -> bool:
        """
        Determine if adaptation should occur now based on frequency settings
        """
        try:
            # Check if enough interactions have occurred since last adaptation
            if last_adaptation:
                interactions_since_adaptation = [
                    i for i in recent_interactions 
                    if i.timestamp > last_adaptation
                ]
            else:
                interactions_since_adaptation = recent_interactions
            
            required_interactions = self.config['adaptation_frequency']
            
            if len(interactions_since_adaptation) < required_interactions:
                return False
            
            # Additional checks for adaptation readiness
            performance_window = self._create_performance_window(
                interactions_since_adaptation[-self.performance_window_size:]
            )
            
            # Don't adapt if performance is too inconsistent
            if len(performance_window.interactions) >= 5:
                metrics = await self._calculate_adaptation_metrics(performance_window, user_profile)
                if metrics['consistency_score'] < 0.3:
                    self.logger.info("Performance too inconsistent for adaptation")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking adaptation timing: {e}")
            return False

    def get_adaptation_history_summary(
        self, 
        adaptations: List[DifficultyAdjustment]
    ) -> Dict[str, Any]:
        """
        Provide a summary of adaptation history
        """
        if not adaptations:
            return {
                'total_adaptations': 0,
                'net_difficulty_change': 0,
                'adaptation_trend': 'none',
                'average_confidence': 0.0
            }
        
        # Calculate trend
        recent_adaptations = adaptations[-5:]  # Last 5 adaptations
        difficulty_changes = [
            adj.new_difficulty - adj.old_difficulty 
            for adj in recent_adaptations
        ]
        
        net_change = sum(difficulty_changes)
        
        if net_change > 1:
            trend = 'increasing'
        elif net_change < -1:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        # Calculate average confidence
        confidence_scores = {
            ConfidenceLevel.LOW: 0.25,
            ConfidenceLevel.MEDIUM: 0.5,
            ConfidenceLevel.HIGH: 0.75,
            ConfidenceLevel.VERY_HIGH: 1.0
        }
        
        avg_confidence = statistics.mean([
            confidence_scores[adj.confidence] for adj in adaptations
        ])
        
        return {
            'total_adaptations': len(adaptations),
            'net_difficulty_change': adaptations[-1].new_difficulty - adaptations[0].old_difficulty,
            'adaptation_trend': trend,
            'average_confidence': avg_confidence,
            'last_adaptation': adaptations[-1].timestamp,
            'most_common_reasons': self._get_most_common_reasons(adaptations)
        }

    def _get_most_common_reasons(self, adaptations: List[DifficultyAdjustment]) -> List[str]:
        """Get the most common reasons for adaptations"""
        reason_counts = {}
        
        for adaptation in adaptations:
            for reason in adaptation.reasoning:
                # Extract key phrases from reasons
                if 'accuracy' in reason.lower():
                    key = 'accuracy_based'
                elif 'time' in reason.lower():
                    key = 'time_based'
                elif 'attempt' in reason.lower():
                    key = 'attempt_based'
                elif 'consistent' in reason.lower():
                    key = 'consistency_based'
                else:
                    key = 'other'
                
                reason_counts[key] = reason_counts.get(key, 0) + 1
        
        # Return top 3 reasons
        sorted_reasons = sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)
        return [reason for reason, _ in sorted_reasons[:3]]