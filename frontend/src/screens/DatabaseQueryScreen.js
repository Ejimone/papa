import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Alert,
  TextInput,
  ActivityIndicator,
  Modal,
} from "react-native";
import { useSelector } from "react-redux";
import { MaterialIcons } from "@expo/vector-icons";
import { adminService } from "../api";

const DatabaseQueryScreen = ({ navigation }) => {
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [queryHistory, setQueryHistory] = useState([]);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [selectedTable, setSelectedTable] = useState("");

  const token = useSelector((state) => state.auth.token);

  const predefinedQueries = [
    {
      id: 1,
      name: "All Users",
      query: "SELECT id, username, email, created_at FROM users ORDER BY created_at DESC LIMIT 10;",
      description: "Get recent users",
    },
    {
      id: 2,
      name: "Active Questions",
      query: "SELECT id, title, subject, difficulty, created_at FROM questions WHERE is_active = true ORDER BY created_at DESC LIMIT 10;",
      description: "Get active questions",
    },
    {
      id: 3,
      name: "User Statistics",
      query: "SELECT COUNT(*) as total_users, COUNT(CASE WHEN is_active = true THEN 1 END) as active_users FROM users;",
      description: "Get user statistics",
    },
    {
      id: 4,
      name: "Question Statistics",
      query: "SELECT subject, COUNT(*) as question_count FROM questions GROUP BY subject ORDER BY question_count DESC;",
      description: "Questions by subject",
    },
    {
      id: 5,
      name: "Recent Uploads",
      query: "SELECT id, original_filename, file_type, created_at FROM uploads ORDER BY created_at DESC LIMIT 10;",
      description: "Recent file uploads",
    },
    {
      id: 6,
      name: "User Activity",
      query: "SELECT u.username, COUNT(ua.id) as attempts FROM users u LEFT JOIN user_attempts ua ON u.id = ua.user_id GROUP BY u.id, u.username ORDER BY attempts DESC LIMIT 10;",
      description: "Most active users",
    },
  ];

  const databaseTables = [
    { name: "users", description: "User accounts and profiles" },
    { name: "questions", description: "Questions and their metadata" },
    { name: "subjects", description: "Subject categories" },
    { name: "uploads", description: "File uploads and processing" },
    { name: "user_attempts", description: "User question attempts" },
    { name: "user_bookmarks", description: "User bookmarked questions" },
    { name: "explanations", description: "Question explanations" },
    { name: "hints", description: "Question hints" },
    { name: "course_materials", description: "Course materials for RAG" },
  ];

  useEffect(() => {
    loadQueryHistory();
  }, []);

  const loadQueryHistory = async () => {
    try {
      // Load query history from local storage or API
      const mockHistory = [
        {
          id: 1,
          query: "SELECT COUNT(*) FROM users;",
          timestamp: new Date().toISOString(),
          success: true,
        },
        {
          id: 2,
          query: "SELECT * FROM questions WHERE difficulty = 'hard';",
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          success: true,
        },
      ];
      setQueryHistory(mockHistory);
    } catch (error) {
      console.error("Error loading query history:", error);
    }
  };

  const executeQuery = async (queryText = query) => {
    if (!queryText.trim()) {
      Alert.alert("Error", "Please enter a query");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setResults(null);

      const response = await adminService.executeQuery(queryText);
      setResults(response);

      // Add to history
      const newHistoryItem = {
        id: Date.now(),
        query: queryText,
        timestamp: new Date().toISOString(),
        success: true,
      };
      setQueryHistory([newHistoryItem, ...queryHistory]);
    } catch (error) {
      console.error("Error executing query:", error);
      setError(error.message || "Failed to execute query");
      
      // Add failed query to history
      const newHistoryItem = {
        id: Date.now(),
        query: queryText,
        timestamp: new Date().toISOString(),
        success: false,
        error: error.message,
      };
      setQueryHistory([newHistoryItem, ...queryHistory]);
    } finally {
      setLoading(false);
    }
  };

  const generateMockResults = (query) => {
    const lowerQuery = query.toLowerCase();
    
    if (lowerQuery.includes("users")) {
      return {
        columns: ["id", "username", "email", "created_at"],
        rows: [
          [1, "john_doe", "john@example.com", "2024-01-15"],
          [2, "jane_smith", "jane@example.com", "2024-01-16"],
          [3, "mike_wilson", "mike@example.com", "2024-01-17"],
        ],
        rowCount: 3,
      };
    }
    
    if (lowerQuery.includes("questions")) {
      return {
        columns: ["id", "title", "subject", "difficulty"],
        rows: [
          [1, "Basic Algebra", "math", "easy"],
          [2, "Newton's Laws", "physics", "medium"],
          [3, "Chemical Bonding", "chemistry", "hard"],
        ],
        rowCount: 3,
      };
    }
    
    if (lowerQuery.includes("count")) {
      return {
        columns: ["count"],
        rows: [[1250]],
        rowCount: 1,
      };
    }
    
    return {
      columns: ["result"],
      rows: [["Query executed successfully"]],
      rowCount: 1,
    };
  };

  const clearQuery = () => {
    setQuery("");
    setResults(null);
    setError(null);
  };

  const loadPredefinedQuery = (predefinedQuery) => {
    setQuery(predefinedQuery.query);
    setResults(null);
    setError(null);
  };

  const loadFromHistory = (historyItem) => {
    setQuery(historyItem.query);
    setResults(null);
    setError(null);
    setShowHistoryModal(false);
  };

  const getTableSchema = (tableName) => {
    // Mock table schema
    const schemas = {
      users: [
        { column: "id", type: "INTEGER", description: "Primary key" },
        { column: "username", type: "VARCHAR(50)", description: "Unique username" },
        { column: "email", type: "VARCHAR(100)", description: "Email address" },
        { column: "is_active", type: "BOOLEAN", description: "Account status" },
        { column: "created_at", type: "TIMESTAMP", description: "Registration date" },
      ],
      questions: [
        { column: "id", type: "INTEGER", description: "Primary key" },
        { column: "title", type: "VARCHAR(200)", description: "Question title" },
        { column: "content", type: "TEXT", description: "Question content" },
        { column: "subject", type: "VARCHAR(50)", description: "Subject category" },
        { column: "difficulty", type: "VARCHAR(20)", description: "Difficulty level" },
        { column: "is_active", type: "BOOLEAN", description: "Question status" },
      ],
    };
    
    return schemas[tableName] || [];
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

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
        <Text style={styles.title}>Database Query</Text>
        <TouchableOpacity
          style={styles.historyButton}
          onPress={() => setShowHistoryModal(true)}
        >
          <MaterialIcons name="history" size={24} color="#007bff" />
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content}>
        {/* Query Input */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>SQL Query</Text>
          <TextInput
            style={styles.queryInput}
            value={query}
            onChangeText={setQuery}
            placeholder="Enter your SQL query here..."
            multiline
            numberOfLines={6}
            textAlignVertical="top"
          />
          <View style={styles.queryActions}>
            <TouchableOpacity
              style={styles.clearButton}
              onPress={clearQuery}
            >
              <MaterialIcons name="clear" size={20} color="#666" />
              <Text style={styles.clearButtonText}>Clear</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.executeButton}
              onPress={executeQuery}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator size="small" color="#fff" />
              ) : (
                <MaterialIcons name="play-arrow" size={20} color="#fff" />
              )}
              <Text style={styles.executeButtonText}>Execute</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Results */}
        {error && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Error</Text>
            <View style={styles.errorContainer}>
              <MaterialIcons name="error" size={24} color="#F44336" />
              <Text style={styles.errorText}>{error}</Text>
            </View>
          </View>
        )}

        {results && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Results ({results.rowCount} rows)</Text>
            <ScrollView horizontal style={styles.resultsContainer}>
              <View>
                {/* Header */}
                <View style={styles.resultHeader}>
                  {results.columns.map((column, index) => (
                    <Text key={index} style={styles.resultHeaderCell}>
                      {column}
                    </Text>
                  ))}
                </View>
                {/* Rows */}
                {results.rows.map((row, rowIndex) => (
                  <View key={rowIndex} style={styles.resultRow}>
                    {row.map((cell, cellIndex) => (
                      <Text key={cellIndex} style={styles.resultCell}>
                        {cell !== null ? cell.toString() : "NULL"}
                      </Text>
                    ))}
                  </View>
                ))}
              </View>
            </ScrollView>
          </View>
        )}

        {/* Predefined Queries */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Predefined Queries</Text>
          <View style={styles.predefinedQueries}>
            {predefinedQueries.map((pq) => (
              <TouchableOpacity
                key={pq.id}
                style={styles.predefinedQueryCard}
                onPress={() => loadPredefinedQuery(pq)}
              >
                <Text style={styles.predefinedQueryName}>{pq.name}</Text>
                <Text style={styles.predefinedQueryDescription}>
                  {pq.description}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Database Schema */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Database Tables</Text>
          <View style={styles.tablesContainer}>
            {databaseTables.map((table) => (
              <TouchableOpacity
                key={table.name}
                style={styles.tableCard}
                onPress={() => setSelectedTable(
                  selectedTable === table.name ? "" : table.name
                )}
              >
                <View style={styles.tableHeader}>
                  <Text style={styles.tableName}>{table.name}</Text>
                  <MaterialIcons
                    name={selectedTable === table.name ? "expand-less" : "expand-more"}
                    size={24}
                    color="#666"
                  />
                </View>
                <Text style={styles.tableDescription}>{table.description}</Text>
                
                {selectedTable === table.name && (
                  <View style={styles.schemaContainer}>
                    {getTableSchema(table.name).map((column, index) => (
                      <View key={index} style={styles.schemaRow}>
                        <Text style={styles.columnName}>{column.column}</Text>
                        <Text style={styles.columnType}>{column.type}</Text>
                        <Text style={styles.columnDescription}>{column.description}</Text>
                      </View>
                    ))}
                  </View>
                )}
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </ScrollView>

      {/* History Modal */}
      <Modal
        visible={showHistoryModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowHistoryModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Query History</Text>
              <TouchableOpacity
                onPress={() => setShowHistoryModal(false)}
              >
                <MaterialIcons name="close" size={24} color="#666" />
              </TouchableOpacity>
            </View>
            
            <ScrollView style={styles.historyList}>
              {queryHistory.map((item) => (
                <TouchableOpacity
                  key={item.id}
                  style={styles.historyItem}
                  onPress={() => loadFromHistory(item)}
                >
                  <View style={styles.historyHeader}>
                    <Text style={styles.historyTimestamp}>
                      {formatTimestamp(item.timestamp)}
                    </Text>
                    <MaterialIcons
                      name={item.success ? "check-circle" : "error"}
                      size={16}
                      color={item.success ? "#4CAF50" : "#F44336"}
                    />
                  </View>
                  <Text style={styles.historyQuery} numberOfLines={2}>
                    {item.query}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f5f5f5",
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
  historyButton: {
    padding: 4,
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
  queryInput: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    fontFamily: "monospace",
    backgroundColor: "#f8f9fa",
    minHeight: 120,
  },
  queryActions: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginTop: 12,
  },
  clearButton: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: "#f5f5f5",
  },
  clearButtonText: {
    color: "#666",
    fontSize: 14,
  },
  executeButton: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: "#007bff",
  },
  executeButtonText: {
    color: "#fff",
    fontSize: 14,
    fontWeight: "500",
  },
  errorContainer: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    padding: 12,
    backgroundColor: "#ffebee",
    borderRadius: 8,
  },
  errorText: {
    flex: 1,
    color: "#F44336",
    fontSize: 14,
  },
  resultsContainer: {
    backgroundColor: "#f8f9fa",
    borderRadius: 8,
    padding: 8,
  },
  resultHeader: {
    flexDirection: "row",
    backgroundColor: "#e9ecef",
    borderRadius: 4,
    marginBottom: 4,
  },
  resultHeaderCell: {
    padding: 8,
    fontSize: 14,
    fontWeight: "600",
    color: "#333",
    minWidth: 100,
    borderRightWidth: 1,
    borderRightColor: "#dee2e6",
  },
  resultRow: {
    flexDirection: "row",
    backgroundColor: "#fff",
    borderRadius: 4,
    marginBottom: 2,
  },
  resultCell: {
    padding: 8,
    fontSize: 14,
    color: "#666",
    minWidth: 100,
    borderRightWidth: 1,
    borderRightColor: "#dee2e6",
  },
  predefinedQueries: {
    gap: 12,
  },
  predefinedQueryCard: {
    padding: 12,
    backgroundColor: "#f8f9fa",
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#e9ecef",
  },
  predefinedQueryName: {
    fontSize: 16,
    fontWeight: "600",
    color: "#333",
    marginBottom: 4,
  },
  predefinedQueryDescription: {
    fontSize: 14,
    color: "#666",
  },
  tablesContainer: {
    gap: 12,
  },
  tableCard: {
    padding: 12,
    backgroundColor: "#f8f9fa",
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#e9ecef",
  },
  tableHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 4,
  },
  tableName: {
    fontSize: 16,
    fontWeight: "600",
    color: "#333",
  },
  tableDescription: {
    fontSize: 14,
    color: "#666",
  },
  schemaContainer: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: "#e9ecef",
  },
  schemaRow: {
    flexDirection: "row",
    paddingVertical: 4,
    gap: 12,
  },
  columnName: {
    fontSize: 14,
    fontWeight: "500",
    color: "#333",
    flex: 1,
  },
  columnType: {
    fontSize: 12,
    color: "#007bff",
    flex: 1,
  },
  columnDescription: {
    fontSize: 12,
    color: "#666",
    flex: 2,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0, 0, 0, 0.5)",
    justifyContent: "center",
    alignItems: "center",
  },
  modalContent: {
    backgroundColor: "#fff",
    borderRadius: 12,
    width: "90%",
    maxHeight: "70%",
  },
  modalHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: "#e0e0e0",
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: "600",
    color: "#333",
  },
  historyList: {
    padding: 16,
  },
  historyItem: {
    padding: 12,
    backgroundColor: "#f8f9fa",
    borderRadius: 8,
    marginBottom: 8,
  },
  historyHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 4,
  },
  historyTimestamp: {
    fontSize: 12,
    color: "#666",
  },
  historyQuery: {
    fontSize: 14,
    color: "#333",
    fontFamily: "monospace",
  },
});

export default DatabaseQueryScreen;
