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

const UploadManagementScreen = ({ navigation }) => {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [uploads, setUploads] = useState([]);
  const [filteredUploads, setFilteredUploads] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterType, setFilterType] = useState("all");
  const [filterStatus, setFilterStatus] = useState("all");
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedUpload, setSelectedUpload] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const token = useSelector((state) => state.auth.token);

  useEffect(() => {
    loadUploads();
  }, []);

  useEffect(() => {
    loadUploads();
  }, [currentPage, filterType, filterStatus, searchQuery]);

  const loadUploads = async () => {
    try {
      setLoading(true);
      const response = await adminService.getAdminUploads(
        currentPage,
        10,
        searchQuery,
        filterType === "all" ? "" : filterType,
        filterStatus === "all" ? "" : filterStatus
      );
      
      setUploads(response.uploads);
      setFilteredUploads(response.uploads);
      setTotalPages(response.total_pages);
      setLoading(false);
      setRefreshing(false);
    } catch (error) {
      console.error("Error loading uploads:", error);
      Alert.alert("Error", "Failed to load uploads");
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadUploads();
  };

  const handleReprocess = async (uploadId) => {
    try {
      Alert.alert(
        "Reprocess File",
        "Are you sure you want to reprocess this file?",
        [
          { text: "Cancel", style: "cancel" },
          {
            text: "Reprocess",
            onPress: async () => {
              try {
                await adminService.reprocessUpload(uploadId);
                Alert.alert("Success", "File queued for reprocessing");
                loadUploads();
              } catch (error) {
                console.error("Error reprocessing upload:", error);
                Alert.alert("Error", "Failed to reprocess file");
              }
            },
          },
        ]
      );
    } catch (error) {
      console.error("Error reprocessing upload:", error);
      Alert.alert("Error", "Failed to reprocess file");
    }
  };

  const handleDeleteUpload = async (uploadId) => {
    try {
      Alert.alert(
        "Delete Upload",
        "Are you sure you want to delete this upload? This action cannot be undone.",
        [
          { text: "Cancel", style: "cancel" },
          {
            text: "Delete",
            style: "destructive",
            onPress: async () => {
              try {
                await adminService.deleteUpload(uploadId);
                Alert.alert("Success", "Upload deleted successfully");
                loadUploads();
              } catch (error) {
                console.error("Error deleting upload:", error);
                Alert.alert("Error", "Failed to delete upload");
              }
            },
          },
        ]
      );
    } catch (error) {
      console.error("Error deleting upload:", error);
      Alert.alert("Error", "Failed to delete upload");
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "completed":
      case "processed":
        return "#4CAF50";
      case "processing":
      case "in_progress":
        return "#FF9800";
      case "failed":
      case "error":
        return "#F44336";
      default:
        return "#9E9E9E";
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "completed":
      case "processed":
        return "check-circle";
      case "processing":
      case "in_progress":
        return "hourglass-empty";
      case "failed":
      case "error":
        return "error";
      default:
        return "help";
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007bff" />
        <Text style={styles.loadingText}>Loading uploads...</Text>
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
        <Text style={styles.title}>Upload Management</Text>
        <TouchableOpacity
          style={styles.refreshButton}
          onPress={onRefresh}
        >
          <MaterialIcons name="refresh" size={24} color="#007bff" />
        </TouchableOpacity>
      </View>

      {/* Search and Filters */}
      <View style={styles.searchContainer}>
        <View style={styles.searchBox}>
          <MaterialIcons name="search" size={20} color="#666" />
          <TextInput
            style={styles.searchInput}
            placeholder="Search uploads..."
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
        </View>
        <View style={styles.filterContainer}>
          <View style={styles.filterRow}>
            <Text style={styles.filterLabel}>Type:</Text>
            <View style={styles.filterButtons}>
              {["all", "pdf", "docx", "txt", "jpg", "png"].map((type) => (
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
            <Text style={styles.filterLabel}>Status:</Text>
            <View style={styles.filterButtons}>
              {["all", "processed", "processing", "failed"].map((status) => (
                <TouchableOpacity
                  key={status}
                  style={[
                    styles.filterButton,
                    filterStatus === status && styles.activeFilter,
                  ]}
                  onPress={() => setFilterStatus(status)}
                >
                  <Text style={styles.filterText}>{status}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        </View>
      </View>

      {/* Upload List */}
      <ScrollView
        style={styles.uploadList}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {filteredUploads.map((upload) => (
          <TouchableOpacity
            key={upload.id}
            style={styles.uploadCard}
            onPress={() => {
              setSelectedUpload(upload);
              setShowDetailModal(true);
            }}
          >
            <View style={styles.uploadInfo}>
              <View style={styles.uploadHeader}>
                <Text style={styles.fileName}>{upload.originalFilename}</Text>
                <View style={styles.uploadBadges}>
                  <View style={styles.typeBadge}>
                    <Text style={styles.typeText}>{upload.fileType}</Text>
                  </View>
                  <View style={[styles.statusBadge, { backgroundColor: getStatusColor(upload.status) }]}>
                    <MaterialIcons 
                      name={getStatusIcon(upload.status)} 
                      size={12} 
                      color="#fff" 
                    />
                    <Text style={styles.statusText}>{upload.status}</Text>
                  </View>
                </View>
              </View>
              <View style={styles.uploadMeta}>
                <Text style={styles.fileSize}>{formatFileSize(upload.fileSize)}</Text>
                <Text style={styles.subject}>{upload.subject}</Text>
                <Text style={styles.questionsCount}>
                  {upload.extractedQuestions} questions
                </Text>
              </View>
              <View style={styles.uploadFooter}>
                <Text style={styles.uploadBy}>
                  By {upload.uploadedBy} • {formatDate(upload.uploadedAt)}
                </Text>
                {upload.errors.length > 0 && (
                  <Text style={styles.errorCount}>
                    {upload.errors.length} error(s)
                  </Text>
                )}
              </View>
            </View>
            <View style={styles.uploadActions}>
              {upload.status === "failed" && (
                <TouchableOpacity
                  style={styles.actionButton}
                  onPress={() => handleReprocess(upload.id)}
                >
                  <MaterialIcons name="refresh" size={20} color="#FF9800" />
                </TouchableOpacity>
              )}
              <TouchableOpacity
                style={styles.actionButton}
                onPress={() => handleDeleteUpload(upload.id)}
              >
                <MaterialIcons name="delete" size={20} color="#F44336" />
              </TouchableOpacity>
            </View>
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
              <Text style={styles.modalTitle}>Upload Details</Text>
              <TouchableOpacity
                onPress={() => setShowDetailModal(false)}
              >
                <MaterialIcons name="close" size={24} color="#666" />
              </TouchableOpacity>
            </View>
            
            {selectedUpload && (
              <ScrollView style={styles.detailContent}>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Filename:</Text>
                  <Text style={styles.detailValue}>{selectedUpload.originalFilename}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>File Type:</Text>
                  <Text style={styles.detailValue}>{selectedUpload.fileType}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>File Size:</Text>
                  <Text style={styles.detailValue}>{formatFileSize(selectedUpload.fileSize)}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Subject:</Text>
                  <Text style={styles.detailValue}>{selectedUpload.subject}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Status:</Text>
                  <Text style={[styles.detailValue, { color: getStatusColor(selectedUpload.status) }]}>
                    {selectedUpload.status}
                  </Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Processing Status:</Text>
                  <Text style={styles.detailValue}>{selectedUpload.processingStatus}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Extracted Questions:</Text>
                  <Text style={styles.detailValue}>{selectedUpload.extractedQuestions}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Uploaded By:</Text>
                  <Text style={styles.detailValue}>{selectedUpload.uploadedBy}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Uploaded At:</Text>
                  <Text style={styles.detailValue}>{formatDate(selectedUpload.uploadedAt)}</Text>
                </View>
                
                {selectedUpload.errors.length > 0 && (
                  <View style={styles.errorsSection}>
                    <Text style={styles.errorsTitle}>Errors:</Text>
                    {selectedUpload.errors.map((error, index) => (
                      <Text key={index} style={styles.errorText}>
                        • {error}
                      </Text>
                    ))}
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
  refreshButton: {
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
  uploadList: {
    flex: 1,
  },
  uploadCard: {
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
  uploadInfo: {
    flex: 1,
  },
  uploadHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 8,
  },
  fileName: {
    fontSize: 16,
    fontWeight: "600",
    color: "#333",
    flex: 1,
    marginRight: 8,
  },
  uploadBadges: {
    flexDirection: "row",
    gap: 4,
  },
  typeBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 12,
    backgroundColor: "#e3f2fd",
  },
  typeText: {
    color: "#1976d2",
    fontSize: 10,
    fontWeight: "bold",
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 12,
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
  },
  statusText: {
    color: "#fff",
    fontSize: 10,
    fontWeight: "bold",
  },
  uploadMeta: {
    flexDirection: "row",
    gap: 12,
    marginBottom: 8,
  },
  fileSize: {
    fontSize: 12,
    color: "#666",
  },
  subject: {
    fontSize: 12,
    color: "#007bff",
    fontWeight: "500",
  },
  questionsCount: {
    fontSize: 12,
    color: "#4CAF50",
    fontWeight: "500",
  },
  uploadFooter: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  uploadBy: {
    fontSize: 12,
    color: "#999",
    flex: 1,
  },
  errorCount: {
    fontSize: 12,
    color: "#F44336",
    fontWeight: "500",
  },
  uploadActions: {
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
    width: "90%",
    maxHeight: "80%",
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
  errorsSection: {
    marginTop: 16,
    padding: 12,
    backgroundColor: "#ffebee",
    borderRadius: 8,
  },
  errorsTitle: {
    fontSize: 14,
    fontWeight: "600",
    color: "#F44336",
    marginBottom: 8,
  },
  errorText: {
    fontSize: 14,
    color: "#F44336",
    marginBottom: 4,
  },
});

export default UploadManagementScreen;
