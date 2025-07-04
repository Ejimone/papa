import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Alert,
  Dimensions,
  ActivityIndicator,
} from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import { useFocusEffect } from '@react-navigation/native';
import {
  selectUser,
  selectIsAuthenticated,
} from '../store/authSlice';
import {
  createPracticeSession,
  fetchProgressSummary,
  selectProgressSummary,
  selectPracticeLoading,
} from '../store/practiceSlice';
import { analyticsService } from '../api/analyticsService';
import { userService } from '../api/userService';
import { practiceService } from '../api/practiceService';
import { aiService } from '../api/aiService';

const { width } = Dimensions.get('window');

const DashboardScreen = ({ navigation }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [userStats, setUserStats] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [recentSessions, setRecentSessions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const dispatch = useDispatch();
  const user = useSelector(selectUser);
  const isAuthenticated = useSelector(selectIsAuthenticated);
  const progressSummary = useSelector(selectProgressSummary);
  const practiceLoading = useSelector(selectPracticeLoading);

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      navigation.replace('Login');
    }
  }, [isAuthenticated, navigation]);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);

      // Load dashboard data in parallel
      const [
        dashboardResponse,
        statsResponse,
        progressResponse,
        sessionsResponse,
      ] = await Promise.allSettled([
        analyticsService.getDashboardData(),
        userService.getUserStatistics(),
        dispatch(fetchProgressSummary()),
        practiceService.getPracticeSessions({ limit: 5 }),
      ]);

      // Handle dashboard data
      if (dashboardResponse.status === 'fulfilled') {
        setDashboardData(dashboardResponse.value);
      }

      // Handle user stats
      if (statsResponse.status === 'fulfilled') {
        setUserStats(statsResponse.value);
      }

      // Handle recent sessions
      if (sessionsResponse.status === 'fulfilled') {
        setRecentSessions(sessionsResponse.value.items || sessionsResponse.value || []);
      }

      // Try to get AI recommendations
      try {
        const recommendationsResponse = await aiService.getRecommendations({
          limit: 3,
          difficulty_range: [1, 3],
        });
        setRecommendations(recommendationsResponse || []);
      } catch (error) {
        console.warn('Failed to load recommendations:', error);
        setRecommendations([]);
      }

    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      Alert.alert('Error', 'Failed to load dashboard data. Please try again.');
    } finally {
      setIsLoading(false);
      setRefreshing(false);
    }
  };

  // Load data when screen comes into focus
  useFocusEffect(
    useCallback(() => {
      loadDashboardData();
    }, [])
  );

  const onRefresh = () => {
    setRefreshing(true);
    loadDashboardData();
  };

  const handleQuickPractice = async (subject = null) => {
    try {
      const sessionConfig = {
        session_type: 'quick_practice',
        question_count: 10,
        difficulty_level: 'mixed',
        ...(subject && { subject_id: subject }),
      };

      const result = await dispatch(createPracticeSession(sessionConfig));
      if (createPracticeSession.fulfilled.match(result)) {
        navigation.navigate('Practice', {
          screen: 'PracticeSession',
          params: { sessionId: result.payload.id },
        });
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to start practice session. Please try again.');
    }
  };

  const handleTimedPractice = () => {
    navigation.navigate('Practice', { screen: 'PracticeSetup', params: { mode: 'timed' } });
  };

  const handleMockTest = () => {
    navigation.navigate('Practice', { screen: 'PracticeSetup', params: { mode: 'mock_test' } });
  };

  const handleViewAnalytics = () => {
    navigation.navigate('Analytics');
  };

  const formatDuration = (minutes) => {
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#3498DB" />
        <Text style={styles.loadingText}>Loading your dashboard...</Text>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.welcomeText}>
          Good {new Date().getHours() < 12 ? 'morning' : 'afternoon'}, {user?.username || user?.email?.split('@')[0] || 'Student'}!
        </Text>
        <Text style={styles.subtitleText}>
          Ready to continue your learning journey?
        </Text>
      </View>

      {/* Quick Stats */}
      {userStats && (
        <View style={styles.statsContainer}>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>{userStats.total_questions_attempted || 0}</Text>
            <Text style={styles.statLabel}>Questions</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>{Math.round(userStats.accuracy_rate || 0)}%</Text>
            <Text style={styles.statLabel}>Accuracy</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>{userStats.current_streak || 0}</Text>
            <Text style={styles.statLabel}>Day Streak</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>
              {formatDuration(userStats.total_study_time_minutes || 0)}
            </Text>
            <Text style={styles.statLabel}>Study Time</Text>
          </View>
        </View>
      )}

      {/* Quick Actions */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Quick Start</Text>
        <View style={styles.quickActionsContainer}>
          <TouchableOpacity
            style={[styles.actionButton, styles.primaryAction]}
            onPress={() => handleQuickPractice()}
            disabled={practiceLoading}
          >
            <Text style={styles.actionButtonText}>Quick Practice</Text>
            <Text style={styles.actionButtonSubtext}>10 questions</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.actionButton, styles.secondaryAction]}
            onPress={handleTimedPractice}
          >
            <Text style={styles.actionButtonTextSecondary}>Timed Practice</Text>
            <Text style={styles.actionButtonSubtextSecondary}>Custom setup</Text>
          </TouchableOpacity>
        </View>

        <TouchableOpacity
          style={[styles.actionButton, styles.mockTestAction]}
          onPress={handleMockTest}
        >
          <Text style={styles.actionButtonText}>Mock Exam</Text>
          <Text style={styles.actionButtonSubtext}>Full assessment</Text>
        </TouchableOpacity>
      </View>

      {/* Progress Summary */}
      {progressSummary && (
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>Your Progress</Text>
            <TouchableOpacity onPress={handleViewAnalytics}>
              <Text style={styles.viewAllText}>View All</Text>
            </TouchableOpacity>
          </View>
          
          <View style={styles.progressContainer}>
            <View style={styles.progressItem}>
              <Text style={styles.progressLabel}>Questions Completed</Text>
              <Text style={styles.progressValue}>
                {progressSummary.total_completed || 0}
              </Text>
            </View>
            <View style={styles.progressItem}>
              <Text style={styles.progressLabel}>Average Score</Text>
              <Text style={styles.progressValue}>
                {Math.round(progressSummary.average_score || 0)}%
              </Text>
            </View>
          </View>
        </View>
      )}

      {/* AI Recommendations */}
      {recommendations.length > 0 && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Recommended For You</Text>
          {recommendations.slice(0, 3).map((rec, index) => (
            <TouchableOpacity
              key={index}
              style={styles.recommendationItem}
              onPress={() => {
                if (rec.subject) {
                  handleQuickPractice(rec.subject);
                }
              }}
            >
              <View style={styles.recommendationContent}>
                <Text style={styles.recommendationTitle}>
                  {rec.strategy || 'Practice Session'}
                </Text>
                <Text style={styles.recommendationDescription}>
                  {rec.reasoning || 'Personalized practice session'}
                </Text>
                <Text style={styles.recommendationConfidence}>
                  Confidence: {Math.round((rec.confidence_score || 0) * 100)}%
                </Text>
              </View>
            </TouchableOpacity>
          ))}
        </View>
      )}

      {/* Recent Sessions */}
      {recentSessions.length > 0 && (
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>Recent Sessions</Text>
            <TouchableOpacity onPress={() => navigation.navigate('Practice', { screen: 'Sessions' })}>
              <Text style={styles.viewAllText}>View All</Text>
            </TouchableOpacity>
          </View>

          {recentSessions.slice(0, 3).map((session, index) => (
            <TouchableOpacity
              key={session.id || index}
              style={styles.sessionItem}
              onPress={() => {
                navigation.navigate('Practice', {
                  screen: 'SessionSummary',
                  params: { sessionId: session.id },
                });
              }}
            >
              <View style={styles.sessionContent}>
                <Text style={styles.sessionTitle}>
                  {session.session_type || 'Practice Session'}
                </Text>
                <Text style={styles.sessionDetails}>
                  {session.subject || 'Mixed'} • {session.questions_count || 0} questions
                </Text>
                <Text style={styles.sessionDate}>
                  {formatDate(session.created_at)}
                </Text>
              </View>
              {session.score !== undefined && (
                <View style={styles.sessionScore}>
                  <Text style={styles.sessionScoreText}>
                    {Math.round(session.score)}%
                  </Text>
                </View>
              )}
            </TouchableOpacity>
          ))}
        </View>
      )}

      {/* Quick Navigation */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Explore</Text>
        <View style={styles.navigationGrid}>
          <TouchableOpacity
            style={styles.navItem}
            onPress={() => navigation.navigate('Subjects')}
          >
            <Text style={styles.navItemTitle}>Browse Subjects</Text>
            <Text style={styles.navItemSubtitle}>Find questions by topic</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={styles.navItem}
            onPress={() => navigation.navigate('Search')}
          >
            <Text style={styles.navItemTitle}>Search Questions</Text>
            <Text style={styles.navItemSubtitle}>Find specific content</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={styles.navItem}
            onPress={() => navigation.navigate('Practice', { screen: 'Bookmarks' })}
          >
            <Text style={styles.navItemTitle}>Bookmarks</Text>
            <Text style={styles.navItemSubtitle}>Your saved questions</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={styles.navItem}
            onPress={() => navigation.navigate('Analytics')}
          >
            <Text style={styles.navItemTitle}>Analytics</Text>
            <Text style={styles.navItemSubtitle}>Track your progress</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F8F9FA',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#7F8C8D',
  },
  header: {
    padding: 20,
    paddingBottom: 10,
  },
  welcomeText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 4,
  },
  subtitleText: {
    fontSize: 16,
    color: '#7F8C8D',
  },
  statsContainer: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    paddingBottom: 10,
    justifyContent: 'space-between',
  },
  statCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    flex: 1,
    marginHorizontal: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statNumber: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#7F8C8D',
    textAlign: 'center',
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    margin: 20,
    marginVertical: 8,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 16,
  },
  viewAllText: {
    fontSize: 14,
    color: '#3498DB',
    fontWeight: '600',
  },
  quickActionsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  actionButton: {
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    flex: 1,
  },
  primaryAction: {
    backgroundColor: '#3498DB',
    marginRight: 6,
  },
  secondaryAction: {
    backgroundColor: '#F8F9FA',
    borderWidth: 1,
    borderColor: '#E1E8ED',
    marginLeft: 6,
  },
  mockTestAction: {
    backgroundColor: '#E74C3C',
  },
  actionButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
  },
  actionButtonTextSecondary: {
    color: '#2C3E50',
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
  },
  actionButtonSubtext: {
    color: '#FFFFFF',
    fontSize: 12,
    opacity: 0.9,
  },
  actionButtonSubtextSecondary: {
    color: '#7F8C8D',
    fontSize: 12,
  },
  progressContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  progressItem: {
    alignItems: 'center',
  },
  progressLabel: {
    fontSize: 14,
    color: '#7F8C8D',
    marginBottom: 8,
  },
  progressValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2C3E50',
  },
  recommendationItem: {
    backgroundColor: '#F8F9FA',
    borderRadius: 8,
    padding: 16,
    marginBottom: 8,
  },
  recommendationContent: {
    flex: 1,
  },
  recommendationTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 4,
  },
  recommendationDescription: {
    fontSize: 14,
    color: '#7F8C8D',
    marginBottom: 8,
    lineHeight: 20,
  },
  recommendationConfidence: {
    fontSize: 12,
    color: '#27AE60',
    fontWeight: '500',
  },
  sessionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#F8F9FA',
    borderRadius: 8,
    padding: 16,
    marginBottom: 8,
  },
  sessionContent: {
    flex: 1,
  },
  sessionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 4,
  },
  sessionDetails: {
    fontSize: 14,
    color: '#7F8C8D',
    marginBottom: 4,
  },
  sessionDate: {
    fontSize: 12,
    color: '#95A5A6',
  },
  sessionScore: {
    backgroundColor: '#27AE60',
    borderRadius: 20,
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  sessionScoreText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  navigationGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  navItem: {
    width: (width - 80) / 2,
    backgroundColor: '#F8F9FA',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
  },
  navItemTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 4,
  },
  navItemSubtitle: {
    fontSize: 12,
    color: '#7F8C8D',
    lineHeight: 16,
  },
});

export default DashboardScreen;