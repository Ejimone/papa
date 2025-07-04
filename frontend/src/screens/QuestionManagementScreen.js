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
  Modal,
  TextInput,
  Switch,
  Picker,
} from "react-native";
import { useSelector } from "react-redux";
import { MaterialIcons } from "@expo/vector-icons";
import { adminService } from "../api";

const QuestionManagementScreen = ({ navigation }) => {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [filteredQuestions, setFilteredQuestions] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [showAddQuestionModal, setShowAddQuestionModal] = useState(false);
  const [showQuestionDetailModal, setShowQuestionDetailModal] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [filterSubject, setFilterSubject] = useState("all");
  const [filterStatus, setFilterStatus] = useState("all");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalQuestions, setTotalQuestions] = useState(0);

  const [newQuestion, setNewQuestion] = useState({
    title: "",
    content: "",
    type: "multiple_choice",
    subject: "",
    difficulty: "medium",
    options: ["", "", "", ""],
    correctAnswer: "",
    explanation: "",
    isActive: true,
  });

  const [subjects, setSubjects] = useState([]);

  const token = useSelector((state) => state.auth.token);

  useEffect(() => {
    loadQuestions();
    loadSubjects();
  }, []);

  useEffect(() => {
    loadQuestions();
  }, [currentPage, filterSubject, filterStatus, searchQuery]);

  const loadSubjects = async () => {
    try {
      // This would come from the subjects API
      const mockSubjects = [
        { id: "math", name: "Mathematics" },
        { id: "physics", name: "Physics" },
        { id: "chemistry", name: "Chemistry" },
        { id: "biology", name: "Biology" },
        { id: "english", name: "English" },
        { id: "history", name: "History" },
      ];
      setSubjects(mockSubjects);
    } catch (error) {
      console.error("Error loading subjects:", error);
    }
  };

  const loadQuestions = async () => {
    try {
      setLoading(true);
      const response = await adminService.getAdminQuestions(
        currentPage,
        10,
        searchQuery,
        filterSubject === "all" ? "" : filterSubject,
        "",
        filterStatus === "all" ? "" : filterStatus
      );
      
      setQuestions(response.questions);
      setFilteredQuestions(response.questions);
      setTotalPages(response.total_pages);
      setTotalQuestions(response.total);
      setLoading(false);
      setRefreshing(false);
    } catch (error) {
      console.error("Error loading questions:", error);
      Alert.alert("Error", "Failed to load questions");
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadQuestions();
  };

  const handleAddQuestion = async () => {
    try {
      if (!newQuestion.title || !newQuestion.content || !newQuestion.subject) {
        Alert.alert("Error", "Please fill in all required fields");
        return;
      }

      await adminService.createQuestion(newQuestion);
      Alert.alert("Success", "Question created successfully");
      setShowAddQuestionModal(false);
      setNewQuestion({
        title: "",
        content: "",
        type: "multiple_choice",
        subject: "",
        difficulty: "medium",
        options: ["", "", "", ""],
        correctAnswer: "",
        explanation: "",
        isActive: true,
      });
      loadQuestions();
    } catch (error) {
      console.error("Error creating question:", error);
      Alert.alert("Error", "Failed to create question");
    }
  };

  const handleToggleQuestionStatus = async (questionId, currentStatus) => {
    try {
      Alert.alert(
        "Confirm",
        `Are you sure you want to ${currentStatus ? "deactivate" : "activate"} this question?`,
        [
          { text: "Cancel", style: "cancel" },
          {
            text: "Confirm",
            onPress: async () => {
              try {
                await adminService.updateQuestion(questionId, { 
                  is_active: !currentStatus 
                });
                Alert.alert("Success", `Question ${currentStatus ? "deactivated" : "activated"} successfully`);
                loadQuestions();
              } catch (error) {
                console.error("Error updating question status:", error);
                Alert.alert("Error", "Failed to update question status");
              }
            },
          },
        ]
      );
    } catch (error) {
      console.error("Error toggling question status:", error);
      Alert.alert("Error", "Failed to update question status");
    }
  };

  const handleDeleteQuestion = async (questionId) => {
    try {
      Alert.alert(
        "Confirm Delete",
        "Are you sure you want to delete this question? This action cannot be undone.",
        [
          { text: "Cancel", style: "cancel" },
          {
            text: "Delete",
            style: "destructive",
            onPress: async () => {
              try {
                await adminService.deleteQuestion(questionId);
                Alert.alert("Success", "Question deleted successfully");
                loadQuestions();
              } catch (error) {
                console.error("Error deleting question:", error);
                Alert.alert("Error", "Failed to delete question");
              }
            },
          },
        ]
      );
    } catch (error) {
      console.error("Error deleting question:", error);
      Alert.alert("Error", "Failed to delete question");
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case "easy":
        return "#4CAF50";
      case "medium":
        return "#FF9800";
      case "hard":
        return "#F44336";
      default:
        return "#9E9E9E";
    }
  };

  const getSubjectName = (subjectId) => {
    const subject = subjects.find(s => s.id === subjectId);
    return subject ? subject.name : subjectId;
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007bff" />
        <Text style={styles.loadingText}>Loading questions...</Text>
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
        <Text style={styles.title}>Question Management</Text>
        <TouchableOpacity
          style={styles.addButton}
          onPress={() => setShowAddQuestionModal(true)}
        >
          <MaterialIcons name="add" size={24} color="#007bff" />
        </TouchableOpacity>
      </View>

      {/* Search and Filters */}
      <View style={styles.searchContainer}>
        <View style={styles.searchBox}>
          <MaterialIcons name="search" size={20} color="#666" />
          <TextInput
            style={styles.searchInput}
            placeholder="Search questions..."
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
        </View>
        <View style={styles.filterContainer}>
          <View style={styles.filterRow}>
            <Text style={styles.filterLabel}>Subject:</Text>
            <View style={styles.filterButtons}>
              <TouchableOpacity
                style={[
                  styles.filterButton,
                  filterSubject === "all" && styles.activeFilter,
                ]}
                onPress={() => setFilterSubject("all")}
              >
                <Text style={styles.filterText}>All</Text>
              </TouchableOpacity>
              {subjects.slice(0, 3).map((subject) => (
                <TouchableOpacity
                  key={subject.id}
                  style={[
                    styles.filterButton,
                    filterSubject === subject.id && styles.activeFilter,
                  ]}
                  onPress={() => setFilterSubject(subject.id)}
                >
                  <Text style={styles.filterText}>{subject.name}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
          <View style={styles.filterRow}>
            <Text style={styles.filterLabel}>Status:</Text>
            <View style={styles.filterButtons}>
              <TouchableOpacity
                style={[
                  styles.filterButton,
                  filterStatus === "all" && styles.activeFilter,
                ]}
                onPress={() => setFilterStatus("all")}
              >
                <Text style={styles.filterText}>All</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[
                  styles.filterButton,
                  filterStatus === "active" && styles.activeFilter,
                ]}
                onPress={() => setFilterStatus("active")}
              >
                <Text style={styles.filterText}>Active</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[
                  styles.filterButton,
                  filterStatus === "inactive" && styles.activeFilter,
                ]}
                onPress={() => setFilterStatus("inactive")}
              >
                <Text style={styles.filterText}>Inactive</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </View>

      {/* Question List */}
      <ScrollView
        style={styles.questionList}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {filteredQuestions.map((question) => (
          <TouchableOpacity
            key={question.id}
            style={styles.questionCard}
            onPress={() => {
              setSelectedQuestion(question);
              setShowQuestionDetailModal(true);
            }}
          >
            <View style={styles.questionInfo}>
              <View style={styles.questionHeader}>
                <Text style={styles.questionTitle}>{question.title}</Text>
                <View style={styles.questionBadges}>
                  <View style={[styles.difficultyBadge, { backgroundColor: getDifficultyColor(question.difficulty) }]}>
                    <Text style={styles.badgeText}>{question.difficulty}</Text>
                  </View>
                  <View style={[
                    styles.statusBadge,
                    { backgroundColor: question.isActive ? "#4CAF50" : "#F44336" }
                  ]}>
                    <Text style={styles.badgeText}>
                      {question.isActive ? "Active" : "Inactive"}
                    </Text>
                  </View>
                </View>
              </View>
              <Text style={styles.questionContent} numberOfLines={2}>
                {question.content}
              </Text>
              <View style={styles.questionMeta}>
                <Text style={styles.subjectText}>
                  {getSubjectName(question.subject)}
                </Text>
                <Text style={styles.statsText}>
                  Views: {question.views} | Attempts: {question.attempts} | 
                  Success: {Math.round(question.correctRate * 100)}%
                </Text>
              </View>
              <Text style={styles.dateText}>
                Created: {formatDate(question.createdAt)} by {question.createdBy}
              </Text>
            </View>
            <View style={styles.questionActions}>
              <TouchableOpacity
                style={styles.actionButton}
                onPress={() => handleToggleQuestionStatus(question.id, question.isActive)}
              >
                <MaterialIcons 
                  name={question.isActive ? "visibility-off" : "visibility"} 
                  size={20} 
                  color={question.isActive ? "#F44336" : "#4CAF50"} 
                />
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.actionButton}
                onPress={() => handleDeleteQuestion(question.id)}
              >
                <MaterialIcons name="delete" size={20} color="#F44336" />
              </TouchableOpacity>
            </View>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Add Question Modal */}
      <Modal
        visible={showAddQuestionModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowAddQuestionModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Add New Question</Text>
              <TouchableOpacity
                onPress={() => setShowAddQuestionModal(false)}
              >
                <MaterialIcons name="close" size={24} color="#666" />
              </TouchableOpacity>
            </View>
            
            <ScrollView style={styles.modalForm}>
              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Title *</Text>
                <TextInput
                  style={styles.textInput}
                  value={newQuestion.title}
                  onChangeText={(text) => setNewQuestion({...newQuestion, title: text})}
                  placeholder="Enter question title"
                />
              </View>
              
              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Content *</Text>
                <TextInput
                  style={[styles.textInput, styles.multilineInput]}
                  value={newQuestion.content}
                  onChangeText={(text) => setNewQuestion({...newQuestion, content: text})}
                  placeholder="Enter question content"
                  multiline
                  numberOfLines={4}
                />
              </View>
              
              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Subject *</Text>
                <View style={styles.pickerContainer}>
                  <Picker
                    selectedValue={newQuestion.subject}
                    onValueChange={(value) => setNewQuestion({...newQuestion, subject: value})}
                  >
                    <Picker.Item label="Select Subject" value="" />
                    {subjects.map((subject) => (
                      <Picker.Item key={subject.id} label={subject.name} value={subject.id} />
                    ))}
                  </Picker>
                </View>
              </View>
              
              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Difficulty</Text>
                <View style={styles.difficultySelector}>
                  {["easy", "medium", "hard"].map((difficulty) => (
                    <TouchableOpacity
                      key={difficulty}
                      style={[
                        styles.difficultyOption,
                        newQuestion.difficulty === difficulty && styles.selectedDifficulty,
                        { borderColor: getDifficultyColor(difficulty) }
                      ]}
                      onPress={() => setNewQuestion({...newQuestion, difficulty})}
                    >
                      <Text style={styles.difficultyOptionText}>{difficulty}</Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>
              
              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Options (for multiple choice)</Text>
                {newQuestion.options.map((option, index) => (
                  <TextInput
                    key={index}
                    style={styles.textInput}
                    value={option}
                    onChangeText={(text) => {
                      const newOptions = [...newQuestion.options];
                      newOptions[index] = text;
                      setNewQuestion({...newQuestion, options: newOptions});
                    }}
                    placeholder={`Option ${index + 1}`}
                  />
                ))}
              </View>
              
              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Correct Answer</Text>
                <TextInput
                  style={styles.textInput}
                  value={newQuestion.correctAnswer}
                  onChangeText={(text) => setNewQuestion({...newQuestion, correctAnswer: text})}
                  placeholder="Enter correct answer"
                />
              </View>
              
              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Explanation</Text>
                <TextInput
                  style={[styles.textInput, styles.multilineInput]}
                  value={newQuestion.explanation}
                  onChangeText={(text) => setNewQuestion({...newQuestion, explanation: text})}
                  placeholder="Enter explanation"
                  multiline
                  numberOfLines={3}
                />
              </View>
              
              <View style={styles.switchGroup}>
                <Text style={styles.inputLabel}>Active</Text>
                <Switch
                  value={newQuestion.isActive}
                  onValueChange={(value) => setNewQuestion({...newQuestion, isActive: value})}
                />
              </View>
            </ScrollView>
            
            <View style={styles.modalActions}>
              <TouchableOpacity
                style={styles.cancelButton}
                onPress={() => setShowAddQuestionModal(false)}
              >
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.confirmButton}
                onPress={handleAddQuestion}
              >
                <Text style={styles.confirmButtonText}>Add Question</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* Question Detail Modal */}
      <Modal
        visible={showQuestionDetailModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowQuestionDetailModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Question Details</Text>
              <TouchableOpacity
                onPress={() => setShowQuestionDetailModal(false)}
              >
                <MaterialIcons name="close" size={24} color="#666" />
              </TouchableOpacity>
            </View>
            
            {selectedQuestion && (
              <ScrollView style={styles.detailContent}>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Title:</Text>
                  <Text style={styles.detailValue}>{selectedQuestion.title}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Content:</Text>
                  <Text style={styles.detailValue}>{selectedQuestion.content}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Subject:</Text>
                  <Text style={styles.detailValue}>{getSubjectName(selectedQuestion.subject)}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Difficulty:</Text>
                  <Text style={[styles.detailValue, { color: getDifficultyColor(selectedQuestion.difficulty) }]}>
                    {selectedQuestion.difficulty}
                  </Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Type:</Text>
                  <Text style={styles.detailValue}>{selectedQuestion.type}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Status:</Text>
                  <Text style={[
                    styles.detailValue,
                    { color: selectedQuestion.isActive ? "#4CAF50" : "#F44336" }
                  ]}>
                    {selectedQuestion.isActive ? "Active" : "Inactive"}
                  </Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Views:</Text>
                  <Text style={styles.detailValue}>{selectedQuestion.views}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Attempts:</Text>
                  <Text style={styles.detailValue}>{selectedQuestion.attempts}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Success Rate:</Text>
                  <Text style={styles.detailValue}>{Math.round(selectedQuestion.correctRate * 100)}%</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Created:</Text>
                  <Text style={styles.detailValue}>{formatDate(selectedQuestion.createdAt)}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Created By:</Text>
                  <Text style={styles.detailValue}>{selectedQuestion.createdBy}</Text>
                </View>
                
                {selectedQuestion.options && selectedQuestion.options.length > 0 && (
                  <View style={styles.optionsSection}>
                    <Text style={styles.optionsTitle}>Options:</Text>
                    {selectedQuestion.options.map((option, index) => (
                      <Text key={index} style={styles.optionText}>
                        {index + 1}. {option}
                      </Text>
                    ))}
                  </View>
                )}
                
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Correct Answer:</Text>
                  <Text style={[styles.detailValue, { color: "#4CAF50", fontWeight: "bold" }]}>
                    {selectedQuestion.correctAnswer}
                  </Text>
                </View>
                
                {selectedQuestion.explanation && (
                  <View style={styles.explanationSection}>
                    <Text style={styles.explanationTitle}>Explanation:</Text>
                    <Text style={styles.explanationText}>{selectedQuestion.explanation}</Text>
                  </View>
                )}
              </ScrollView>
            )}
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
  addButton: {
    padding: 4,
  },
  searchContainer: {
    backgroundColor: "#fff",
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: "#e0e0e0",
  },
  searchBox: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#f5f5f5",
    borderRadius: 8,
    paddingHorizontal: 12,
    marginBottom: 12,
  },
  searchInput: {
    flex: 1,
    height: 40,
    marginLeft: 8,
    fontSize: 16,
  },
  filterContainer: {
    gap: 8,
  },
  filterRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  filterLabel: {
    fontSize: 14,
    color: "#666",
    fontWeight: "500",
    minWidth: 60,
  },
  filterButtons: {
    flexDirection: "row",
    gap: 8,
    flex: 1,
  },
  filterButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    backgroundColor: "#f5f5f5",
  },
  activeFilter: {
    backgroundColor: "#007bff",
  },
  filterText: {
    color: "#666",
    fontSize: 12,
  },
  questionList: {
    flex: 1,
  },
  questionCard: {
    backgroundColor: "#fff",
    margin: 8,
    marginBottom: 0,
    padding: 16,
    borderRadius: 8,
    flexDirection: "row",
    alignItems: "flex-start",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  questionInfo: {
    flex: 1,
  },
  questionHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 8,
  },
  questionTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#333",
    flex: 1,
    marginRight: 8,
  },
  questionBadges: {
    flexDirection: "row",
    gap: 4,
  },
  difficultyBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 12,
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 12,
  },
  badgeText: {
    color: "#fff",
    fontSize: 10,
    fontWeight: "bold",
  },
  questionContent: {
    fontSize: 14,
    color: "#666",
    marginBottom: 8,
    lineHeight: 20,
  },
  questionMeta: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 4,
  },
  subjectText: {
    fontSize: 12,
    color: "#007bff",
    fontWeight: "500",
  },
  statsText: {
    fontSize: 12,
    color: "#666",
  },
  dateText: {
    fontSize: 12,
    color: "#999",
  },
  questionActions: {
    flexDirection: "row",
    gap: 8,
  },
  actionButton: {
    padding: 8,
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
    width: "95%",
    maxHeight: "90%",
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
  modalForm: {
    padding: 16,
  },
  inputGroup: {
    marginBottom: 16,
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: "500",
    color: "#333",
    marginBottom: 8,
  },
  textInput: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 16,
    marginBottom: 8,
  },
  multilineInput: {
    height: 80,
    textAlignVertical: "top",
  },
  pickerContainer: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 8,
    marginBottom: 8,
  },
  difficultySelector: {
    flexDirection: "row",
    gap: 8,
  },
  difficultyOption: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: "#f5f5f5",
    borderWidth: 1,
  },
  selectedDifficulty: {
    backgroundColor: "#e3f2fd",
  },
  difficultyOptionText: {
    color: "#666",
    fontSize: 14,
  },
  switchGroup: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 16,
  },
  modalActions: {
    flexDirection: "row",
    gap: 12,
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: "#e0e0e0",
  },
  cancelButton: {
    flex: 1,
    padding: 12,
    borderRadius: 8,
    backgroundColor: "#f5f5f5",
    alignItems: "center",
  },
  cancelButtonText: {
    color: "#666",
    fontSize: 16,
    fontWeight: "500",
  },
  confirmButton: {
    flex: 1,
    padding: 12,
    borderRadius: 8,
    backgroundColor: "#007bff",
    alignItems: "center",
  },
  confirmButtonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "500",
  },
  detailContent: {
    padding: 16,
  },
  detailRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: "#f0f0f0",
  },
  detailLabel: {
    fontSize: 14,
    color: "#666",
    fontWeight: "500",
    flex: 1,
  },
  detailValue: {
    fontSize: 14,
    color: "#333",
    flex: 2,
    textAlign: "right",
  },
  optionsSection: {
    marginVertical: 16,
    padding: 12,
    backgroundColor: "#f9f9f9",
    borderRadius: 8,
  },
  optionsTitle: {
    fontSize: 14,
    fontWeight: "600",
    color: "#333",
    marginBottom: 8,
  },
  optionText: {
    fontSize: 14,
    color: "#666",
    marginBottom: 4,
  },
  explanationSection: {
    marginVertical: 16,
    padding: 12,
    backgroundColor: "#f0f8ff",
    borderRadius: 8,
  },
  explanationTitle: {
    fontSize: 14,
    fontWeight: "600",
    color: "#333",
    marginBottom: 8,
  },
  explanationText: {
    fontSize: 14,
    color: "#666",
    lineHeight: 20,
  },
});

export default QuestionManagementScreen;
