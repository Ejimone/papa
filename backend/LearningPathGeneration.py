import datetime
from datetime import datetime

class LearningPathGenerator:
    def __init__(self):
        self.curriculum_mapper = CurriculumMapper()
        self.dependency_analyzer = TopicDependencyAnalyzer()
        self.progress_optimizer = ProgressOptimizer()
    
    async def generate_study_plan(self, user_id: str, goals: StudyGoals) -> StudyPlan:
        # Analyze user's current knowledge state
        knowledge_state = await self.analyze_knowledge_state(user_id, goals.subjects)
        
        # Map curriculum dependencies
        curriculum_graph = await self.curriculum_mapper.build_dependency_graph(
            goals.subjects
        )
        
        # Identify optimal learning sequence
        learning_sequence = await self.dependency_analyzer.calculate_optimal_sequence(
            curriculum_graph, knowledge_state
        )
        
        # Generate time-based study schedule
        study_schedule = await self.progress_optimizer.create_schedule(
            learning_sequence=learning_sequence,
            available_time=goals.study_time_per_day,
            target_date=goals.exam_date,
            user_learning_speed=knowledge_state.learning_speed
        )
        
        # Create adaptive milestones
        milestones = await self.create_adaptive_milestones(
            study_schedule, knowledge_state
        )
        
        return StudyPlan(
            user_id=user_id,
            subjects=goals.subjects,
            learning_sequence=learning_sequence,
            study_schedule=study_schedule,
            milestones=milestones,
            created_at=datetime.utcnow(),
            target_exam_date=goals.exam_date
        )
    
    async def update_study_plan(self, user_id: str, recent_performance: List[UserAttempt]) -> StudyPlan:
        # Get current study plan
        current_plan = await self.get_current_study_plan(user_id)
        
        # Analyze recent performance
        performance_analysis = await self.analyze_recent_performance(recent_performance)
        
        # Adjust learning sequence based on performance
        adjusted_sequence = await self.adjust_learning_sequence(
            current_plan.learning_sequence,
            performance_analysis
        )
        
        # Recalculate study schedule
        updated_schedule = await self.recalculate_schedule(
            current_plan, adjusted_sequence, performance_analysis.learning_speed_change
        )
        
        return StudyPlan(
            user_id=user_id,
            subjects=current_plan.subjects,
            learning_sequence=adjusted_sequence,
            study_schedule=updated_schedule,
            milestones=await self.update_milestones(current_plan.milestones, performance_analysis),
            created_at=current_plan.created_at,
            updated_at=datetime.utcnow(),
            target_exam_date=current_plan.target_exam_date
        )