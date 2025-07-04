import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Alert,
  ActivityIndicator,
  RefreshControl,
} from "react-native";
import { useSelector } from "react-redux";
import { MaterialIcons } from "@expo/vector-icons";

const AdminDashboardScreen = ({ navigation }) => {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalQuestions: 0,
    totalUploads: 0,
    activeUsers: 0,
    pendingReviews: 0,
    systemHealth: "good",
  });

  const user = useSelector((state) => state.auth.user);
  const token = useSelector((state) => state.auth.token);

  useEffect(() => {
    loadAdminStats();
  }, []);

  const loadAdminStats = async () => {
    try {
      setLoading(true);
      
      // Fetch real admin dashboard data
      const response = await fetch("http://172.16.17.124:8000/api/v1/admin/dashboard", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch admin stats");
      }

      const data = await response.json();
      
      setStats({
        totalUsers: data.total_users || 0,
        totalQuestions: data.total_questions || 0,
        totalUploads: data.total_course_materials || 0,
        activeUsers: data.active_sessions || 0,
        pendingReviews: data.recent_uploads || 0,
        systemHealth: data.system_status === "healthy" ? "good" : "warning",
      });
      
    } catch (error) {
      console.error("Error loading admin stats:", error);
      Alert.alert(
        "Error", 
        "Failed to load admin statistics. Please check your admin privileges.",
        [{ text: "OK" }]
      );
      
      // Fallback to mock data
      setStats({
        totalUsers: 0,
        totalQuestions: 0,
        totalUploads: 0,
        activeUsers: 0,
        pendingReviews: 0,
        systemHealth: "warning",
      });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadAdminStats();
  };

  const adminFeatures = [
    {
      id: "users",
      title: "User Management",
      description: "View, add, and manage users",
      icon: "people",
      color: "#4CAF50",
      badge: stats.totalUsers,
      onPress: () => navigation.navigate("UserManagement"),
    },
    {
      id: "questions",
      title: "Question Management",
      description: "Add, edit, and review questions",
      icon: "quiz",
      color: "#2196F3",
      badge: stats.totalQuestions,
      onPress: () => navigation.navigate("QuestionManagement"),
    },
    {
      id: "analytics",
      title: "Analytics & Reports",
      description: "View app analytics and reports",
      icon: "analytics",
      color: "#FF9800",
      badge: null,
      onPress: () => navigation.navigate("AdminAnalytics"),
    },
    {
      id: "database",
      title: "Database Query",
      description: "Query and manage database",
      icon: "storage",
      color: "#9C27B0",
      badge: null,
      onPress: () => navigation.navigate("DatabaseQuery"),
    },
    {
      id: "uploads",
      title: "File Uploads",
      description: "Manage uploaded files",
      icon: "cloud-upload",
      color: "#607D8B",
      badge: stats.totalUploads,
      onPress: () => navigation.navigate("UploadManagement"),
    },
    {
      id: "reviews",
      title: "Content Review",
      description: "Review pending content",
      icon: "rate-review",
      color: "#F44336",
      badge: stats.pendingReviews,
      onPress: () => navigation.navigate("ContentReview"),
    },
    {
      id: "settings",
      title: "System Settings",
      description: "Configure app settings",
      icon: "settings",
      color: "#795548",
      badge: null,
      onPress: () => navigation.navigate("SystemSettings"),
    },
    {
      id: "logs",
      title: "System Logs",
      description: "View system logs and errors",
      icon: "description",
      color: "#E91E63",
      badge: null,
      onPress: () => navigation.navigate("SystemLogs"),
    },
  ];

  const getHealthColor = (health) => {
    switch (health) {
      case "good":
        return "#4CAF50";
      case "warning":
        return "#FF9800";
      case "error":
        return "#F44336";
      default:
        return "#9E9E9E";
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007bff" />
        <Text style={styles.loadingText}>Loading admin dashboard...</Text>
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
      <View style={styles.header}>
        <Text style={styles.title}>Admin Dashboard</Text>
        <Text style={styles.subtitle}>Welcome back, {user?.username || "Admin"}</Text>
      </View>

      {/* System Health Status */}
      <View style={styles.healthCard}>
        <View style={styles.healthHeader}>
          <MaterialIcons name="health-and-safety" size={24} color={getHealthColor(stats.systemHealth)} />
          <Text style={styles.healthTitle}>System Health</Text>
        </View>
        <View style={[styles.healthIndicator, { backgroundColor: getHealthColor(stats.systemHealth) }]}>
          <Text style={styles.healthStatus}>{stats.systemHealth.toUpperCase()}</Text>
        </View>
      </View>

      {/* Quick Stats */}
      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <MaterialIcons name="people" size={24} color="#4CAF50" />
          <Text style={styles.statValue}>{stats.totalUsers}</Text>
          <Text style={styles.statLabel}>Total Users</Text>
        </View>
        <View style={styles.statCard}>
          <MaterialIcons name="quiz" size={24} color="#2196F3" />
          <Text style={styles.statValue}>{stats.totalQuestions}</Text>
          <Text style={styles.statLabel}>Questions</Text>
        </View>
        <View style={styles.statCard}>
          <MaterialIcons name="cloud-upload" size={24} color="#FF9800" />
          <Text style={styles.statValue}>{stats.totalUploads}</Text>
          <Text style={styles.statLabel}>Uploads</Text>
        </View>
        <View style={styles.statCard}>
          <MaterialIcons name="trending-up" size={24} color="#9C27B0" />
          <Text style={styles.statValue}>{stats.activeUsers}</Text>
          <Text style={styles.statLabel}>Active Now</Text>
        </View>
      </View>

      {/* Admin Features */}
      <View style={styles.featuresContainer}>
        <Text style={styles.sectionTitle}>Admin Features</Text>
        <View style={styles.featuresGrid}>
          {adminFeatures.map((feature) => (
            <TouchableOpacity
              key={feature.id}
              style={styles.featureCard}
              onPress={feature.onPress}
            >
              <View style={styles.featureHeader}>
                <MaterialIcons name={feature.icon} size={28} color={feature.color} />
                {feature.badge && (
                  <View style={[styles.badge, { backgroundColor: feature.color }]}>
                    <Text style={styles.badgeText}>{feature.badge}</Text>
                  </View>
                )}
              </View>
              <Text style={styles.featureTitle}>{feature.title}</Text>
              <Text style={styles.featureDescription}>{feature.description}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Recent Activity */}
      <View style={styles.activityContainer}>
        <Text style={styles.sectionTitle}>Recent Activity</Text>
        <View style={styles.activityCard}>
          <View style={styles.activityItem}>
            <MaterialIcons name="person-add" size={20} color="#4CAF50" />
            <Text style={styles.activityText}>5 new users registered today</Text>
          </View>
          <View style={styles.activityItem}>
            <MaterialIcons name="upload" size={20} color="#2196F3" />
            <Text style={styles.activityText}>12 new questions uploaded</Text>
          </View>
          <View style={styles.activityItem}>
            <MaterialIcons name="rate-review" size={20} color="#FF9800" />
            <Text style={styles.activityText}>{stats.pendingReviews} items pending review</Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f5f5f5",
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#f5f5f5",
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: "#666",
  },
  header: {
    backgroundColor: "#fff",
    padding: 20,
    paddingTop: 40,
    borderBottomWidth: 1,
    borderBottomColor: "#e0e0e0",
  },
  title: {
    fontSize: 28,
    fontWeight: "bold",
    color: "#333",
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: "#666",
  },
  healthCard: {
    backgroundColor: "#fff",
    margin: 16,
    padding: 16,
    borderRadius: 12,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  healthHeader: {
    flexDirection: "row",
    alignItems: "center",
  },
  healthTitle: {
    fontSize: 18,
    fontWeight: "600",
    color: "#333",
    marginLeft: 8,
  },
  healthIndicator: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  healthStatus: {
    color: "#fff",
    fontSize: 12,
    fontWeight: "bold",
  },
  statsContainer: {
    flexDirection: "row",
    paddingHorizontal: 16,
    gap: 12,
  },
  statCard: {
    flex: 1,
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 12,
    alignItems: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statValue: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#333",
    marginTop: 8,
  },
  statLabel: {
    fontSize: 12,
    color: "#666",
    marginTop: 4,
    textAlign: "center",
  },
  featuresContainer: {
    margin: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: "600",
    color: "#333",
    marginBottom: 16,
  },
  featuresGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 12,
  },
  featureCard: {
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 12,
    width: "48%",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  featureHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  badge: {
    borderRadius: 10,
    paddingHorizontal: 8,
    paddingVertical: 2,
    minWidth: 20,
    alignItems: "center",
  },
  badgeText: {
    color: "#fff",
    fontSize: 10,
    fontWeight: "bold",
  },
  featureTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#333",
    marginBottom: 4,
  },
  featureDescription: {
    fontSize: 12,
    color: "#666",
    lineHeight: 16,
  },
  activityContainer: {
    margin: 16,
    marginTop: 0,
  },
  activityCard: {
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 12,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  activityItem: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 8,
  },
  activityText: {
    fontSize: 14,
    color: "#666",
    marginLeft: 12,
  },
});

export default AdminDashboardScreen;
