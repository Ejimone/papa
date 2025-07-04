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
} from "react-native";
import { useSelector } from "react-redux";
import { MaterialIcons } from "@expo/vector-icons";
import { adminService } from "../api";

const ContentReviewScreen = ({ navigation }) => {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [reviewItems, setReviewItems] = useState([]);
  const [filteredItems, setFilteredItems] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterType, setFilterType] = useState("all");
  const [filterPriority, setFilterPriority] = useState("all");
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [moderatorNotes, setModeratorNotes] = useState("");

  const token = useSelector((state) => state.auth.token);

  useEffect(() => {
    loadReviewItems();
  }, []);

  useEffect(() => {
    loadReviewItems();
  }, [currentPage, filterType, filterPriority]);

  const loadReviewItems = async () => {
    try {
      setLoading(true);
      const response = await adminService.getContentReview(
        currentPage,
        10,
        filterType === "all" ? "all" : filterType,
        "pending"
      );
      
      setReviewItems(response.items);
      setFilteredItems(response.items);
      setTotalPages(response.total_pages);
      setLoading(false);
      setRefreshing(false);
    } catch (error) {
      console.error("Error loading review items:", error);
      // Fallback to mock data on error
      const mockItems = [
        {
          id: 1,
          type: "question",
          title: "Physics - Quantum Mechanics",
          content: "What is the uncertainty principle in quantum mechanics?",
          submittedBy: "student_user",
          submittedAt: "2024-01-20T10:30:00Z",
          priority: "high",
          status: "pending",
          subject: "physics",
          flags: ["inappropriate_content"],
          moderatorNotes: "",
        },
        {
          id: 2,
          type: "explanation",
          title: "Mathematics - Calculus Solution",
          content: "Step-by-step solution for integral calculus problem...",
          submittedBy: "teacher_user",
          submittedAt: "2024-01-20T14:15:00Z",
          priority: "medium",
          status: "pending",
          subject: "mathematics",
          flags: ["accuracy_check"],
          moderatorNotes: "",
        },
      ];
      setReviewItems(mockItems);
      setFilteredItems(mockItems);
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadReviewItems();
  };

  const handleApproveContent = async (itemId) => {
    try {
      Alert.alert(
        "Approve Content",
        "Are you sure you want to approve this content?",
        [
          { text: "Cancel", style: "cancel" },
          {
            text: "Approve",
            onPress: async () => {
              try {
                await adminService.approveContent(itemId, moderatorNotes);
                Alert.alert("Success", "Content approved successfully");
                loadReviewItems();
                setModeratorNotes("");
              } catch (error) {
                console.error("Error approving content:", error);
                Alert.alert("Error", "Failed to approve content");
              }
            },
          },
        ]
      );
    } catch (error) {
      console.error("Error approving content:", error);
      Alert.alert("Error", "Failed to approve content");
    }
  };

  const handleRejectContent = async (itemId, reason) => {
    try {
      Alert.alert(
        "Reject Content",
        "Are you sure you want to reject this content?",
        [
          { text: "Cancel", style: "cancel" },
          {
            text: "Reject",
            style: "destructive",
            onPress: async () => {
              try {
                await adminService.rejectContent(itemId, reason, moderatorNotes);
                Alert.alert("Success", "Content rejected successfully");
                loadReviewItems();
                setModeratorNotes("");
              } catch (error) {
                console.error("Error rejecting content:", error);
                Alert.alert("Error", "Failed to reject content");
              }
            },
          },
        ]
      );
    } catch (error) {
      console.error("Error rejecting content:", error);
      Alert.alert("Error", "Failed to reject content");
    }
  };

  const filterItems = () => {
    let filtered = reviewItems;

    if (filterStatus !== "all") {
      filtered = filtered.filter((item) => item.status === filterStatus);
    }

    if (filterType !== "all") {
      filtered = filtered.filter((item) => item.type === filterType);
    }

    if (filterPriority !== "all") {
      filtered = filtered.filter((item) => item.priority === filterPriority);
    }

    setFilteredItems(filtered);
  };

  const handleFlag = async (itemId, flag) => {
    try {
      setReviewItems(reviewItems.map(item => 
        item.id === itemId 
          ? { ...item, flags: [...item.flags, flag] }
          : item
      ));
      Alert.alert("Success", "Content flagged successfully");
    } catch (error) {
      console.error("Error flagging content:", error);
      Alert.alert("Error", "Failed to flag content");
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case "high":
        return "#F44336";
      case "medium":
        return "#FF9800";
      case "low":
        return "#4CAF50";
      default:
        return "#9E9E9E";
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "approved":
        return "#4CAF50";
      case "rejected":
        return "#F44336";
      case "pending":
        return "#FF9800";
      default:
        return "#9E9E9E";
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case "question":
        return "quiz";
      case "explanation":
        return "description";
      case "upload":
        return "cloud-upload";
      default:
        return "help";
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007bff" />
        <Text style={styles.loadingText}>Loading review items...</Text>
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
        <Text style={styles.title}>Content Review</Text>
        <View style={styles.headerBadge}>
          <Text style={styles.headerBadgeText}>
            {reviewItems.filter(item => item.status === "pending").length}
          </Text>
        </View>
      </View>

      {/* Search and Filters */}
      <View style={styles.searchContainer}>
        <View style={styles.searchBox}>
          <MaterialIcons name="search" size={20} color="#666" />
          <TextInput
            style={styles.searchInput}
            placeholder="Search content..."
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
        </View>
        <View style={styles.filterContainer}>
          <View style={styles.filterRow}>
            <Text style={styles.filterLabel}>Type:</Text>
            <View style={styles.filterButtons}>
              {["all", "question", "explanation", "upload"].map((type) => (
                <TouchableOpacity
                  key={type}
                  style={[
                    styles.filterButton,
                    filterType === type && styles.activeFilter,
                  ]}
                  onPress={() => setFilterType(type)}
                >
                  <Text style={styles.filterText}>{type}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
          <View style={styles.filterRow}>
            <Text style={styles.filterLabel}>Priority:</Text>
            <View style={styles.filterButtons}>
              {["all", "high", "medium", "low"].map((priority) => (
                <TouchableOpacity
                  key={priority}
                  style={[
                    styles.filterButton,
                    filterPriority === priority && styles.activeFilter,
                  ]}
                  onPress={() => setFilterPriority(priority)}
                >
                  <Text style={styles.filterText}>{priority}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        </View>
      </View>

      {/* Review Items List */}
      <ScrollView
        style={styles.reviewList}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {filteredItems.map((item) => (
          <TouchableOpacity
            key={item.id}
            style={styles.reviewCard}
            onPress={() => {
              setSelectedItem(item);
              setShowDetailModal(true);
            }}
          >
            <View style={styles.reviewInfo}>
              <View style={styles.reviewHeader}>
                <View style={styles.titleRow}>
                  <MaterialIcons 
                    name={getTypeIcon(item.type)} 
                    size={20} 
                    color="#666" 
                  />
                  <Text style={styles.reviewTitle}>{item.title}</Text>
                </View>
                <View style={styles.reviewBadges}>
                  <View style={[styles.priorityBadge, { backgroundColor: getPriorityColor(item.priority) }]}>
                    <Text style={styles.badgeText}>{item.priority}</Text>
                  </View>
                  <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
                    <Text style={styles.badgeText}>{item.status}</Text>
                  </View>
                </View>
              </View>
              <Text style={styles.reviewContent} numberOfLines={2}>
                {item.content}
              </Text>
              <View style={styles.reviewMeta}>
                <Text style={styles.subjectText}>{item.subject}</Text>
                <Text style={styles.submittedBy}>
                  By {item.submittedBy} • {formatDate(item.submittedAt)}
                </Text>
              </View>
              {item.flags.length > 0 && (
                <View style={styles.flagsContainer}>
                  <MaterialIcons name="flag" size={16} color="#F44336" />
                  <Text style={styles.flagsText}>
                    Flags: {item.flags.join(", ")}
                  </Text>
                </View>
              )}
            </View>
            
            {item.status === "pending" && (
              <View style={styles.reviewActions}>
                <TouchableOpacity
                  style={[styles.actionButton, styles.approveButton]}
                  onPress={() => handleApprove(item.id)}
                >
                  <MaterialIcons name="check" size={20} color="#fff" />
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.actionButton, styles.rejectButton]}
                  onPress={() => handleReject(item.id)}
                >
                  <MaterialIcons name="close" size={20} color="#fff" />
                </TouchableOpacity>
              </View>
            )}
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Detail Modal */}
      <Modal
        visible={showDetailModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowDetailModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Content Review Details</Text>
              <TouchableOpacity
                onPress={() => setShowDetailModal(false)}
              >
                <MaterialIcons name="close" size={24} color="#666" />
              </TouchableOpacity>
            </View>
            
            {selectedItem && (
              <ScrollView style={styles.detailContent}>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Type:</Text>
                  <Text style={styles.detailValue}>{selectedItem.type}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Title:</Text>
                  <Text style={styles.detailValue}>{selectedItem.title}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Subject:</Text>
                  <Text style={styles.detailValue}>{selectedItem.subject}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Priority:</Text>
                  <Text style={[styles.detailValue, { color: getPriorityColor(selectedItem.priority) }]}>
                    {selectedItem.priority}
                  </Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Status:</Text>
                  <Text style={[styles.detailValue, { color: getStatusColor(selectedItem.status) }]}>
                    {selectedItem.status}
                  </Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Submitted By:</Text>
                  <Text style={styles.detailValue}>{selectedItem.submittedBy}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Submitted At:</Text>
                  <Text style={styles.detailValue}>{formatDate(selectedItem.submittedAt)}</Text>
                </View>
                
                <View style={styles.contentSection}>
                  <Text style={styles.contentTitle}>Content:</Text>
                  <Text style={styles.contentText}>{selectedItem.content}</Text>
                </View>
                
                {selectedItem.flags.length > 0 && (
                  <View style={styles.flagsSection}>
                    <Text style={styles.flagsTitle}>Flags:</Text>
                    {selectedItem.flags.map((flag, index) => (
                      <Text key={index} style={styles.flagItem}>
                        • {flag}
                      </Text>
                    ))}
                  </View>
                )}
                
                {selectedItem.moderatorNotes && (
                  <View style={styles.notesSection}>
                    <Text style={styles.notesTitle}>Moderator Notes:</Text>
                    <Text style={styles.notesText}>{selectedItem.moderatorNotes}</Text>
                  </View>
                )}
                
                {selectedItem.status === "pending" && (
                  <View style={styles.modalActions}>
                    <TouchableOpacity
                      style={styles.modalApproveButton}
                      onPress={() => {
                        handleApprove(selectedItem.id);
                        setShowDetailModal(false);
                      }}
                    >
                      <MaterialIcons name="check" size={20} color="#fff" />
                      <Text style={styles.modalActionText}>Approve</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                      style={styles.modalRejectButton}
                      onPress={() => {
                        handleReject(selectedItem.id);
                        setShowDetailModal(false);
                      }}
                    >
                      <MaterialIcons name="close" size={20} color="#fff" />
                      <Text style={styles.modalActionText}>Reject</Text>
                    </TouchableOpacity>
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
  headerBadge: {
    backgroundColor: "#F44336",
    borderRadius: 12,
    paddingHorizontal: 8,
    paddingVertical: 4,
    minWidth: 24,
    alignItems: "center",
  },
  headerBadgeText: {
    color: "#fff",
    fontSize: 12,
    fontWeight: "bold",
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
    flexWrap: "wrap",
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
  reviewList: {
    flex: 1,
  },
  reviewCard: {
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
  reviewInfo: {
    flex: 1,
  },
  reviewHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: 8,
  },
  titleRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    flex: 1,
    marginRight: 8,
  },
  reviewTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#333",
    flex: 1,
  },
  reviewBadges: {
    flexDirection: "row",
    gap: 4,
  },
  priorityBadge: {
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
  reviewContent: {
    fontSize: 14,
    color: "#666",
    marginBottom: 8,
    lineHeight: 20,
  },
  reviewMeta: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 4,
  },
  subjectText: {
    fontSize: 12,
    color: "#007bff",
    fontWeight: "500",
  },
  submittedBy: {
    fontSize: 12,
    color: "#999",
  },
  flagsContainer: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    marginTop: 4,
  },
  flagsText: {
    fontSize: 12,
    color: "#F44336",
  },
  reviewActions: {
    flexDirection: "row",
    gap: 8,
  },
  actionButton: {
    padding: 8,
    borderRadius: 20,
    alignItems: "center",
    justifyContent: "center",
  },
  approveButton: {
    backgroundColor: "#4CAF50",
  },
  rejectButton: {
    backgroundColor: "#F44336",
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
  contentSection: {
    marginVertical: 16,
    padding: 12,
    backgroundColor: "#f9f9f9",
    borderRadius: 8,
  },
  contentTitle: {
    fontSize: 14,
    fontWeight: "600",
    color: "#333",
    marginBottom: 8,
  },
  contentText: {
    fontSize: 14,
    color: "#666",
    lineHeight: 20,
  },
  flagsSection: {
    marginVertical: 16,
    padding: 12,
    backgroundColor: "#ffebee",
    borderRadius: 8,
  },
  flagsTitle: {
    fontSize: 14,
    fontWeight: "600",
    color: "#F44336",
    marginBottom: 8,
  },
  flagItem: {
    fontSize: 14,
    color: "#F44336",
    marginBottom: 4,
  },
  notesSection: {
    marginVertical: 16,
    padding: 12,
    backgroundColor: "#e3f2fd",
    borderRadius: 8,
  },
  notesTitle: {
    fontSize: 14,
    fontWeight: "600",
    color: "#1976d2",
    marginBottom: 8,
  },
  notesText: {
    fontSize: 14,
    color: "#1976d2",
    lineHeight: 20,
  },
  modalActions: {
    flexDirection: "row",
    gap: 12,
    marginTop: 16,
  },
  modalApproveButton: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
    padding: 12,
    borderRadius: 8,
    backgroundColor: "#4CAF50",
  },
  modalRejectButton: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
    padding: 12,
    borderRadius: 8,
    backgroundColor: "#F44336",
  },
  modalActionText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "500",
  },
});

export default ContentReviewScreen;
