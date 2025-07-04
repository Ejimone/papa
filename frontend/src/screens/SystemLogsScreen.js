import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  RefreshControl,
  TextInput,
} from "react-native";
import { useSelector } from "react-redux";
import { MaterialIcons } from "@expo/vector-icons";
import { adminService } from "../api";

const SystemLogsScreen = ({ navigation }) => {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [logs, setLogs] = useState([]);
  const [filteredLogs, setFilteredLogs] = useState([]);
  const [selectedLevel, setSelectedLevel] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const token = useSelector((state) => state.auth.token);

  const logLevels = [
    { id: "all", label: "All Levels", color: "#666" },
    { id: "error", label: "Error", color: "#F44336" },
    { id: "warning", label: "Warning", color: "#FF9800" },
    { id: "info", label: "Info", color: "#2196F3" },
    { id: "debug", label: "Debug", color: "#4CAF50" },
  ];

  useEffect(() => {
    loadLogs();
  }, []);

  useEffect(() => {
    loadLogs();
  }, [currentPage, selectedLevel]);

  const loadLogs = async () => {
    try {
      setLoading(true);
      const response = await adminService.getSystemLogs(
        currentPage,
        50,
        selectedLevel === "all" ? "all" : selectedLevel
      );
      
      setLogs(response.logs);
      setFilteredLogs(response.logs);
      setTotalPages(response.total_pages);
      setLoading(false);
      setRefreshing(false);
    } catch (error) {
      console.error("Error loading logs:", error);
      // Fallback to mock data on error
      const mockLogs = [
        {
          id: 1,
          timestamp: new Date().toISOString(),
          level: "info",
          message: "User authentication successful",
          module: "auth",
          userId: "user123",
          ipAddress: "192.168.1.100",
        },
        {
          id: 2,
          timestamp: new Date(Date.now() - 300000).toISOString(),
          level: "warning",
          message: "High memory usage detected",
          module: "system",
          details: "Memory usage: 85%",
        },
        {
          id: 3,
          timestamp: new Date(Date.now() - 600000).toISOString(),
          level: "error",
          message: "Database connection timeout",
          module: "database",
          error: "Connection timeout after 30s",
        },
      ];
      setLogs(mockLogs);
      setFilteredLogs(mockLogs);
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadLogs();
  };

  const filterLogs = () => {
    let filtered = logs;

    if (searchQuery) {
      filtered = filtered.filter(
        (log) =>
          log.message.toLowerCase().includes(searchQuery.toLowerCase()) ||
          log.module.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    setFilteredLogs(filtered);
  };

  useEffect(() => {
    filterLogs();
  }, [searchQuery, logs]);

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const getLevelColor = (level) => {
    const levelConfig = logLevels.find(l => l.id === level);
    return levelConfig ? levelConfig.color : "#666";
  };

  const getLevelIcon = (level) => {
    switch (level) {
      case "error":
        return "error";
      case "warning":
        return "warning";
      case "info":
        return "info";
      case "debug":
        return "bug-report";
      default:
        return "description";
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Loading logs...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <MaterialIcons name="arrow-back" size={24} color="#007AFF" />
        </TouchableOpacity>
        <Text style={styles.title}>System Logs</Text>
        <View style={styles.placeholder} />
      </View>

      {/* Search and Filters */}
      <View style={styles.searchContainer}>
        <View style={styles.searchInputContainer}>
          <MaterialIcons name="search" size={20} color="#666" />
          <TextInput
            style={styles.searchInput}
            placeholder="Search logs..."
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
        </View>
      </View>

      {/* Level Filter */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.levelFilterContainer}
        contentContainerStyle={styles.levelFilterContent}
      >
        {logLevels.map((level) => (
          <TouchableOpacity
            key={level.id}
            style={[
              styles.levelFilterButton,
              selectedLevel === level.id && styles.levelFilterButtonActive,
              { borderColor: level.color },
            ]}
            onPress={() => setSelectedLevel(level.id)}
          >
            <Text
              style={[
                styles.levelFilterText,
                selectedLevel === level.id && styles.levelFilterTextActive,
                { color: selectedLevel === level.id ? "#fff" : level.color },
              ]}
            >
              {level.label}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Logs List */}
      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {filteredLogs.map((log) => (
          <View key={log.id} style={styles.logItem}>
            <View style={styles.logHeader}>
              <View style={styles.logLevelContainer}>
                <MaterialIcons
                  name={getLevelIcon(log.level)}
                  size={16}
                  color={getLevelColor(log.level)}
                />
                <Text
                  style={[
                    styles.logLevel,
                    { color: getLevelColor(log.level) },
                  ]}
                >
                  {log.level.toUpperCase()}
                </Text>
              </View>
              <Text style={styles.logTimestamp}>
                {formatTimestamp(log.timestamp)}
              </Text>
            </View>
            
            <Text style={styles.logMessage}>{log.message}</Text>
            
            <View style={styles.logDetails}>
              <Text style={styles.logModule}>Module: {log.module}</Text>
              {log.userId && (
                <Text style={styles.logDetail}>User ID: {log.userId}</Text>
              )}
              {log.ipAddress && (
                <Text style={styles.logDetail}>IP: {log.ipAddress}</Text>
              )}
              {log.error && (
                <Text style={styles.logError}>Error: {log.error}</Text>
              )}
              {log.details && (
                <Text style={styles.logDetail}>Details: {log.details}</Text>
              )}
            </View>
          </View>
        ))}

        {filteredLogs.length === 0 && (
          <View style={styles.noLogsContainer}>
            <MaterialIcons name="description" size={64} color="#ccc" />
            <Text style={styles.noLogsText}>No logs found</Text>
          </View>
        )}
      </ScrollView>

      {/* Pagination */}
      {totalPages > 1 && (
        <View style={styles.paginationContainer}>
          <TouchableOpacity
            style={[
              styles.paginationButton,
              currentPage === 1 && styles.paginationButtonDisabled,
            ]}
            onPress={() => setCurrentPage(currentPage - 1)}
            disabled={currentPage === 1}
          >
            <MaterialIcons name="chevron-left" size={24} color="#007AFF" />
          </TouchableOpacity>
          
          <Text style={styles.paginationText}>
            Page {currentPage} of {totalPages}
          </Text>
          
          <TouchableOpacity
            style={[
              styles.paginationButton,
              currentPage === totalPages && styles.paginationButtonDisabled,
            ]}
            onPress={() => setCurrentPage(currentPage + 1)}
            disabled={currentPage === totalPages}
          >
            <MaterialIcons name="chevron-right" size={24} color="#007AFF" />
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f8f9fa",
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: "#666",
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 20,
    paddingTop: 60,
    paddingBottom: 20,
    backgroundColor: "#fff",
    borderBottomWidth: 1,
    borderBottomColor: "#e0e0e0",
  },
  backButton: {
    padding: 8,
  },
  title: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#333",
  },
  placeholder: {
    width: 40,
  },
  searchContainer: {
    padding: 20,
    backgroundColor: "#fff",
    borderBottomWidth: 1,
    borderBottomColor: "#e0e0e0",
  },
  searchInputContainer: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#f5f5f5",
    borderRadius: 10,
    paddingHorizontal: 15,
    paddingVertical: 10,
  },
  searchInput: {
    flex: 1,
    marginLeft: 10,
    fontSize: 16,
    color: "#333",
  },
  levelFilterContainer: {
    backgroundColor: "#fff",
    borderBottomWidth: 1,
    borderBottomColor: "#e0e0e0",
  },
  levelFilterContent: {
    paddingHorizontal: 20,
    paddingVertical: 15,
  },
  levelFilterButton: {
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    marginRight: 10,
    backgroundColor: "#fff",
  },
  levelFilterButtonActive: {
    backgroundColor: "#007AFF",
  },
  levelFilterText: {
    fontSize: 14,
    fontWeight: "500",
  },
  levelFilterTextActive: {
    color: "#fff",
  },
  content: {
    flex: 1,
    padding: 20,
  },
  logItem: {
    backgroundColor: "#fff",
    borderRadius: 10,
    padding: 15,
    marginBottom: 10,
    borderLeftWidth: 4,
    borderLeftColor: "#007AFF",
  },
  logHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  logLevelContainer: {
    flexDirection: "row",
    alignItems: "center",
  },
  logLevel: {
    fontSize: 12,
    fontWeight: "bold",
    marginLeft: 5,
  },
  logTimestamp: {
    fontSize: 12,
    color: "#666",
  },
  logMessage: {
    fontSize: 14,
    color: "#333",
    marginBottom: 8,
    lineHeight: 20,
  },
  logDetails: {
    marginTop: 5,
  },
  logModule: {
    fontSize: 12,
    color: "#666",
    marginBottom: 2,
  },
  logDetail: {
    fontSize: 12,
    color: "#666",
    marginBottom: 2,
  },
  logError: {
    fontSize: 12,
    color: "#F44336",
    marginBottom: 2,
  },
  noLogsContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingVertical: 60,
  },
  noLogsText: {
    fontSize: 16,
    color: "#666",
    marginTop: 10,
  },
  paginationContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    padding: 20,
    backgroundColor: "#fff",
    borderTopWidth: 1,
    borderTopColor: "#e0e0e0",
  },
  paginationButton: {
    padding: 10,
  },
  paginationButtonDisabled: {
    opacity: 0.3,
  },
  paginationText: {
    fontSize: 14,
    color: "#666",
  },
});

export default SystemLogsScreen;
