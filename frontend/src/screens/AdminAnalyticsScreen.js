import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  RefreshControl,
  Dimensions,
} from "react-native";
import { useSelector } from "react-redux";
import { MaterialIcons } from "@expo/vector-icons";
import { LineChart, BarChart, PieChart } from "react-native-chart-kit";
import { adminService } from "../api";

const { width: screenWidth } = Dimensions.get("window");

const AdminAnalyticsScreen = ({ navigation }) => {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedTimeRange, setSelectedTimeRange] = useState("7d");
  const [analytics, setAnalytics] = useState({
    userGrowth: [],
    questionStats: [],
    subjectPopularity: [],
    systemMetrics: {},
    activityData: [],
  });

  const token = useSelector((state) => state.auth.token);

  useEffect(() => {
    loadAnalytics();
  }, [selectedTimeRange]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const response = await adminService.getAdminAnalytics(selectedTimeRange);
      
      // Transform the data for chart display
      const transformedData = {
        userGrowth: {
          labels: response.user_growth?.labels || ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
          datasets: [
            {
              data: response.user_growth?.data || [20, 45, 28, 80, 99, 43],
              color: (opacity = 1) => `rgba(134, 65, 244, ${opacity})`,
              strokeWidth: 2,
            },
          ],
        },
        questionStats: {
          labels: response.question_stats?.labels || ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
          datasets: [
            {
              data: response.question_stats?.data || [20, 45, 28, 80, 99, 43, 67],
              color: (opacity = 1) => `rgba(255, 99, 132, ${opacity})`,
              strokeWidth: 2,
            },
          ],
        },
        subjectPopularity: response.subject_popularity?.map(item => ({
          name: item.name,
          population: item.percentage,
          color: item.color,
          legendFontColor: "#7F7F7F",
          legendFontSize: 15,
        })) || [
          {
            name: "Mathematics",
            population: 35,
            color: "#FF6384",
            legendFontColor: "#7F7F7F",
            legendFontSize: 15,
          },
          {
            name: "Physics",
            population: 25,
            color: "#36A2EB",
            legendFontColor: "#7F7F7F",
            legendFontSize: 15,
          },
          {
            name: "Chemistry",
            population: 20,
            color: "#FFCE56",
            legendFontColor: "#7F7F7F",
            legendFontSize: 15,
          },
          {
            name: "Biology",
            population: 15,
            color: "#4BC0C0",
            legendFontColor: "#7F7F7F",
            legendFontSize: 15,
          },
          {
            name: "Others",
            population: 5,
            color: "#9966FF",
            legendFontColor: "#7F7F7F",
            legendFontSize: 15,
          },
        ],
        systemMetrics: response.system_metrics || {
          totalUsers: 1250,
          activeUsers: 856,
          totalQuestions: 5680,
          totalUploads: 892,
          avgResponseTime: 245,
          uptime: 99.8,
          storageUsed: 78.5,
          cpuUsage: 32.1,
        },
        activityData: response.activity_data || [
          { time: "00:00", users: 12, questions: 8 },
          { time: "04:00", users: 6, questions: 3 },
          { time: "08:00", users: 45, questions: 67 },
          { time: "12:00", users: 123, questions: 156 },
          { time: "16:00", users: 89, questions: 134 },
          { time: "20:00", users: 67, questions: 89 },
        ],
      };
      
      setAnalytics(transformedData);
      setLoading(false);
      setRefreshing(false);
    } catch (error) {
      console.error("Error loading analytics:", error);
      // Fallback to mock data on error
      setAnalytics({
        userGrowth: {
          labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
          datasets: [
            {
              data: [20, 45, 28, 80, 99, 43],
              color: (opacity = 1) => `rgba(134, 65, 244, ${opacity})`,
              strokeWidth: 2,
            },
          ],
        },
        questionStats: {
          labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
          datasets: [
            {
              data: [20, 45, 28, 80, 99, 43, 67],
              color: (opacity = 1) => `rgba(255, 99, 132, ${opacity})`,
              strokeWidth: 2,
            },
          ],
        },
        subjectPopularity: [
          {
            name: "Mathematics",
            population: 35,
            color: "#FF6384",
            legendFontColor: "#7F7F7F",
            legendFontSize: 15,
          },
          {
            name: "Physics",
            population: 25,
            color: "#36A2EB",
            legendFontColor: "#7F7F7F",
            legendFontSize: 15,
          },
          {
            name: "Chemistry",
            population: 20,
            color: "#FFCE56",
            legendFontColor: "#7F7F7F",
            legendFontSize: 15,
          },
          {
            name: "Biology",
            population: 15,
            color: "#4BC0C0",
            legendFontColor: "#7F7F7F",
            legendFontSize: 15,
          },
          {
            name: "Others",
            population: 5,
            color: "#9966FF",
            legendFontColor: "#7F7F7F",
            legendFontSize: 15,
          },
        ],
        systemMetrics: {
          totalUsers: 1250,
          activeUsers: 856,
          totalQuestions: 5680,
          totalUploads: 892,
          avgResponseTime: 245,
          uptime: 99.8,
          storageUsed: 78.5,
          cpuUsage: 32.1,
        },
        activityData: [
          { time: "00:00", users: 12, questions: 8 },
          { time: "04:00", users: 6, questions: 3 },
          { time: "08:00", users: 45, questions: 67 },
          { time: "12:00", users: 123, questions: 156 },
          { time: "16:00", users: 89, questions: 134 },
          { time: "20:00", users: 67, questions: 89 },
        ],
      });
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadAnalytics();
  };

  const timeRanges = [
    { id: "1d", label: "24h" },
    { id: "7d", label: "7d" },
    { id: "30d", label: "30d" },
    { id: "90d", label: "90d" },
  ];

  const chartConfig = {
    backgroundGradientFrom: "#ffffff",
    backgroundGradientFromOpacity: 0,
    backgroundGradientTo: "#ffffff",
    backgroundGradientToOpacity: 0,
    color: (opacity = 1) => `rgba(0, 123, 255, ${opacity})`,
    strokeWidth: 2,
    barPercentage: 0.5,
    useShadowColorFromDataset: false,
    decimalPlaces: 0,
  };

  const getHealthColor = (value, type) => {
    if (type === "uptime") {
      return value >= 99 ? "#4CAF50" : value >= 95 ? "#FF9800" : "#F44336";
    }
    if (type === "cpu" || type === "storage") {
      return value <= 50 ? "#4CAF50" : value <= 80 ? "#FF9800" : "#F44336";
    }
    return "#4CAF50";
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007bff" />
        <Text style={styles.loadingText}>Loading analytics...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <MaterialIcons name="arrow-back" size={24} color="#333" />
        </TouchableOpacity>
        <Text style={styles.title}>Analytics & Reports</Text>
        <TouchableOpacity
          style={styles.exportButton}
          onPress={() => {
            // TODO: Implement export functionality
            console.log("Export analytics");
          }}
        >
          <MaterialIcons name="file-download" size={24} color="#007bff" />
        </TouchableOpacity>
      </View>

      {/* Time Range Selector */}
      <View style={styles.timeRangeContainer}>
        <Text style={styles.timeRangeLabel}>Time Range:</Text>
        <View style={styles.timeRangeButtons}>
          {timeRanges.map((range) => (
            <TouchableOpacity
              key={range.id}
              style={[
                styles.timeRangeButton,
                selectedTimeRange === range.id && styles.activeTimeRange,
              ]}
              onPress={() => setSelectedTimeRange(range.id)}
            >
              <Text style={[
                styles.timeRangeText,
                selectedTimeRange === range.id && styles.activeTimeRangeText,
              ]}>
                {range.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* System Metrics */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>System Metrics</Text>
          <View style={styles.metricsGrid}>
            <View style={styles.metricCard}>
              <MaterialIcons name="people" size={24} color="#4CAF50" />
              <Text style={styles.metricValue}>{analytics.systemMetrics.totalUsers}</Text>
              <Text style={styles.metricLabel}>Total Users</Text>
            </View>
            <View style={styles.metricCard}>
              <MaterialIcons name="trending-up" size={24} color="#2196F3" />
              <Text style={styles.metricValue}>{analytics.systemMetrics.activeUsers}</Text>
              <Text style={styles.metricLabel}>Active Users</Text>
            </View>
            <View style={styles.metricCard}>
              <MaterialIcons name="quiz" size={24} color="#FF9800" />
              <Text style={styles.metricValue}>{analytics.systemMetrics.totalQuestions}</Text>
              <Text style={styles.metricLabel}>Questions</Text>
            </View>
            <View style={styles.metricCard}>
              <MaterialIcons name="cloud-upload" size={24} color="#9C27B0" />
              <Text style={styles.metricValue}>{analytics.systemMetrics.totalUploads}</Text>
              <Text style={styles.metricLabel}>Uploads</Text>
            </View>
          </View>
        </View>

        {/* Performance Metrics */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Performance Metrics</Text>
          <View style={styles.performanceGrid}>
            <View style={styles.performanceCard}>
              <View style={styles.performanceHeader}>
                <MaterialIcons name="speed" size={20} color="#666" />
                <Text style={styles.performanceTitle}>Response Time</Text>
              </View>
              <Text style={styles.performanceValue}>{analytics.systemMetrics.avgResponseTime}ms</Text>
            </View>
            <View style={styles.performanceCard}>
              <View style={styles.performanceHeader}>
                <MaterialIcons name="health-and-safety" size={20} color="#666" />
                <Text style={styles.performanceTitle}>Uptime</Text>
              </View>
              <Text style={[
                styles.performanceValue,
                { color: getHealthColor(analytics.systemMetrics.uptime, "uptime") }
              ]}>
                {analytics.systemMetrics.uptime}%
              </Text>
            </View>
            <View style={styles.performanceCard}>
              <View style={styles.performanceHeader}>
                <MaterialIcons name="storage" size={20} color="#666" />
                <Text style={styles.performanceTitle}>Storage Used</Text>
              </View>
              <Text style={[
                styles.performanceValue,
                { color: getHealthColor(analytics.systemMetrics.storageUsed, "storage") }
              ]}>
                {analytics.systemMetrics.storageUsed}%
              </Text>
            </View>
            <View style={styles.performanceCard}>
              <View style={styles.performanceHeader}>
                <MaterialIcons name="memory" size={20} color="#666" />
                <Text style={styles.performanceTitle}>CPU Usage</Text>
              </View>
              <Text style={[
                styles.performanceValue,
                { color: getHealthColor(analytics.systemMetrics.cpuUsage, "cpu") }
              ]}>
                {analytics.systemMetrics.cpuUsage}%
              </Text>
            </View>
          </View>
        </View>

        {/* User Growth Chart */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>User Growth</Text>
          <View style={styles.chartContainer}>
            <LineChart
              data={analytics.userGrowth}
              width={screenWidth - 32}
              height={220}
              chartConfig={chartConfig}
              bezier
              style={styles.chart}
            />
          </View>
        </View>

        {/* Question Activity Chart */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Question Activity</Text>
          <View style={styles.chartContainer}>
            <BarChart
              data={analytics.questionStats}
              width={screenWidth - 32}
              height={220}
              chartConfig={chartConfig}
              style={styles.chart}
            />
          </View>
        </View>

        {/* Subject Popularity */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Subject Popularity</Text>
          <View style={styles.chartContainer}>
            <PieChart
              data={analytics.subjectPopularity}
              width={screenWidth - 32}
              height={220}
              chartConfig={chartConfig}
              accessor="population"
              backgroundColor="transparent"
              paddingLeft="15"
              style={styles.chart}
            />
          </View>
        </View>

        {/* Activity Summary */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Activity Summary</Text>
          <View style={styles.activityContainer}>
            {analytics.activityData.map((item, index) => (
              <View key={index} style={styles.activityItem}>
                <Text style={styles.activityTime}>{item.time}</Text>
                <View style={styles.activityBars}>
                  <View style={styles.activityBar}>
                    <View style={[
                      styles.activityBarFill,
                      { 
                        width: `${(item.users / 150) * 100}%`,
                        backgroundColor: "#4CAF50" 
                      }
                    ]} />
                  </View>
                  <Text style={styles.activityValue}>{item.users} users</Text>
                </View>
                <View style={styles.activityBars}>
                  <View style={styles.activityBar}>
                    <View style={[
                      styles.activityBarFill,
                      { 
                        width: `${(item.questions / 200) * 100}%`,
                        backgroundColor: "#2196F3" 
                      }
                    ]} />
                  </View>
                  <Text style={styles.activityValue}>{item.questions} questions</Text>
                </View>
              </View>
            ))}
          </View>
        </View>

        {/* Export Options */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Export Options</Text>
          <View style={styles.exportOptions}>
            <TouchableOpacity style={styles.exportOption}>
              <MaterialIcons name="picture-as-pdf" size={24} color="#F44336" />
              <Text style={styles.exportText}>Export as PDF</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.exportOption}>
              <MaterialIcons name="table-chart" size={24} color="#4CAF50" />
              <Text style={styles.exportText}>Export as CSV</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.exportOption}>
              <MaterialIcons name="email" size={24} color="#2196F3" />
              <Text style={styles.exportText}>Email Report</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </View>
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
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: "#666",
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#fff",
    padding: 16,
    paddingTop: 50,
    borderBottomWidth: 1,
    borderBottomColor: "#e0e0e0",
  },
  backButton: {
    marginRight: 16,
  },
  title: {
    flex: 1,
    fontSize: 20,
    fontWeight: "600",
    color: "#333",
  },
  exportButton: {
    padding: 4,
  },
  timeRangeContainer: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#fff",
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: "#e0e0e0",
  },
  timeRangeLabel: {
    fontSize: 16,
    color: "#666",
    marginRight: 16,
  },
  timeRangeButtons: {
    flexDirection: "row",
    gap: 8,
  },
  timeRangeButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: "#f5f5f5",
    borderWidth: 1,
    borderColor: "#ddd",
  },
  activeTimeRange: {
    backgroundColor: "#007bff",
    borderColor: "#007bff",
  },
  timeRangeText: {
    color: "#666",
    fontSize: 14,
  },
  activeTimeRangeText: {
    color: "#fff",
  },
  content: {
    flex: 1,
  },
  section: {
    backgroundColor: "#fff",
    margin: 16,
    marginBottom: 0,
    padding: 16,
    borderRadius: 12,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "600",
    color: "#333",
    marginBottom: 16,
  },
  metricsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 12,
  },
  metricCard: {
    flex: 1,
    minWidth: "45%",
    backgroundColor: "#f8f9fa",
    padding: 16,
    borderRadius: 8,
    alignItems: "center",
    gap: 8,
  },
  metricValue: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#333",
  },
  metricLabel: {
    fontSize: 12,
    color: "#666",
    textAlign: "center",
  },
  performanceGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 12,
  },
  performanceCard: {
    flex: 1,
    minWidth: "45%",
    backgroundColor: "#f8f9fa",
    padding: 12,
    borderRadius: 8,
  },
  performanceHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginBottom: 8,
  },
  performanceTitle: {
    fontSize: 14,
    color: "#666",
  },
  performanceValue: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#333",
  },
  chartContainer: {
    alignItems: "center",
    marginTop: 8,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 8,
  },
  activityContainer: {
    gap: 12,
  },
  activityItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  activityTime: {
    fontSize: 12,
    color: "#666",
    width: 40,
  },
  activityBars: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  activityBar: {
    flex: 1,
    height: 8,
    backgroundColor: "#f0f0f0",
    borderRadius: 4,
  },
  activityBarFill: {
    height: "100%",
    borderRadius: 4,
  },
  activityValue: {
    fontSize: 12,
    color: "#666",
    width: 80,
  },
  exportOptions: {
    flexDirection: "row",
    gap: 16,
  },
  exportOption: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    padding: 12,
    backgroundColor: "#f8f9fa",
    borderRadius: 8,
  },
  exportText: {
    fontSize: 14,
    color: "#666",
  },
});

export default AdminAnalyticsScreen;
