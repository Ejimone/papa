import React, { useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Alert,
  ActivityIndicator,
  TextInput,
  Switch,
} from "react-native";
import { useSelector } from "react-redux";
import * as DocumentPicker from "expo-document-picker";
import * as ImagePicker from "expo-image-picker";
import uploadService from "../api/uploadService";

const CourseMaterialsUploadScreen = ({ navigation }) => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    subject_id: 1, // TODO: Allow user to select subject
    topic_id: null,
    material_type: "lecture_notes",
    tags: "",
    enable_rag: true,
    auto_extract_questions: true,
  });

  const user = useSelector((state) => state.auth.user);
  const token = useSelector((state) => state.auth.token);
  const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);

  const pickDocument = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: [
          "application/pdf",
          "text/plain",
          "application/msword",
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
          "application/vnd.ms-powerpoint",
          "application/vnd.openxmlformats-officedocument.presentationml.presentation",
          "text/markdown",
          "text/html",
        ],
        copyToCacheDirectory: true,
        multiple: true,
      });

      if (!result.canceled && result.assets) {
        const newFiles = result.assets.map((file) => ({
          ...file,
          type: "document",
          id: Date.now() + Math.random(),
        }));
        setSelectedFiles((prev) => [...prev, ...newFiles]);
      }
    } catch (error) {
      Alert.alert("Error", "Failed to pick documents");
    }
  };

  const removeFile = (fileId) => {
    setSelectedFiles((prev) => prev.filter((file) => file.id !== fileId));
  };

  const uploadCourseMaterials = async () => {
    if (selectedFiles.length === 0) {
      Alert.alert("No Files", "Please select at least one file to upload");
      return;
    }

    if (!formData.title.trim()) {
      Alert.alert("Missing Title", "Please provide a title for the course materials");
      return;
    }

    if (!isAuthenticated || !token) {
      Alert.alert(
        "Login Required",
        "Please log in to upload course materials."
      );
      return;
    }

    setUploading(true);

    try {
      // Prepare file objects for upload
      const files = selectedFiles.map((file) => ({
        uri: file.uri,
        type: file.mimeType || "application/pdf",
        name: file.name,
      }));

      // Upload course materials
      const uploadData = {
        ...formData,
        files: files,
      };

      console.log("Uploading course materials with data:", uploadData);

      const result = await uploadService.uploadCourseMaterials(uploadData);

      console.log("Upload result:", result);

      Alert.alert(
        "Upload Successful!",
        `Successfully uploaded ${result.uploaded_files.length} file(s). ` +
        (formData.enable_rag ? "Files will be processed for search functionality. " : "") +
        (formData.auto_extract_questions ? "Questions will be extracted automatically." : ""),
        [
          {
            text: "OK",
            onPress: () => {
              setSelectedFiles([]);
              setFormData({
                title: "",
                description: "",
                subject_id: 1,
                topic_id: null,
                material_type: "lecture_notes",
                tags: "",
                enable_rag: true,
                auto_extract_questions: true,
              });
              navigation.goBack();
            },
          },
        ]
      );
    } catch (error) {
      console.error("Upload error:", error);
      Alert.alert(
        "Upload Failed",
        error.response?.data?.detail || "Failed to upload course materials. Please try again."
      );
    } finally {
      setUploading(false);
    }
  };

  const updateFormData = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Upload Course Materials</Text>
        <Text style={styles.subtitle}>
          Upload lecture notes, textbooks, and other course materials to enhance your learning experience
        </Text>
      </View>

      {/* Form Fields */}
      <View style={styles.formContainer}>
        <Text style={styles.sectionTitle}>Material Information</Text>

        <TextInput
          style={styles.input}
          placeholder="Title (required)"
          value={formData.title}
          onChangeText={(value) => updateFormData("title", value)}
        />

        <TextInput
          style={[styles.input, styles.textArea]}
          placeholder="Description (optional)"
          value={formData.description}
          onChangeText={(value) => updateFormData("description", value)}
          multiline
          numberOfLines={3}
        />

        <TextInput
          style={styles.input}
          placeholder="Tags (comma-separated)"
          value={formData.tags}
          onChangeText={(value) => updateFormData("tags", value)}
        />

        {/* Material Type Selector */}
        <View style={styles.pickerContainer}>
          <Text style={styles.pickerLabel}>Material Type:</Text>
          <View style={styles.pickerButtons}>
            {[
              { key: "lecture_notes", label: "Lecture Notes" },
              { key: "textbook", label: "Textbook" },
              { key: "past_questions", label: "Past Questions" },
              { key: "reference", label: "Reference Material" },
            ].map((type) => (
              <TouchableOpacity
                key={type.key}
                style={[
                  styles.pickerButton,
                  formData.material_type === type.key && styles.pickerButtonActive,
                ]}
                onPress={() => updateFormData("material_type", type.key)}
              >
                <Text
                  style={[
                    styles.pickerButtonText,
                    formData.material_type === type.key && styles.pickerButtonTextActive,
                  ]}
                >
                  {type.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Options */}
        <View style={styles.optionsContainer}>
          <Text style={styles.sectionTitle}>Processing Options</Text>

          <View style={styles.switchContainer}>
            <Text style={styles.switchLabel}>Enable search functionality (RAG)</Text>
            <Switch
              value={formData.enable_rag}
              onValueChange={(value) => updateFormData("enable_rag", value)}
            />
          </View>

          <View style={styles.switchContainer}>
            <Text style={styles.switchLabel}>Auto-extract questions</Text>
            <Switch
              value={formData.auto_extract_questions}
              onValueChange={(value) => updateFormData("auto_extract_questions", value)}
            />
          </View>
        </View>
      </View>

      {/* File Upload */}
      <View style={styles.uploadSection}>
        <Text style={styles.sectionTitle}>Upload Files</Text>

        <TouchableOpacity style={styles.uploadButton} onPress={pickDocument}>
          <Text style={styles.uploadButtonIcon}>📄</Text>
          <View style={styles.uploadButtonContent}>
            <Text style={styles.uploadButtonTitle}>Select Documents</Text>
            <Text style={styles.uploadButtonSubtitle}>
              PDF, Word, PowerPoint, or Text files
            </Text>
          </View>
        </TouchableOpacity>
      </View>

      {/* Selected Files */}
      {selectedFiles.length > 0 && (
        <View style={styles.selectedFiles}>
          <Text style={styles.sectionTitle}>
            Selected Files ({selectedFiles.length})
          </Text>
          {selectedFiles.map((file) => (
            <View key={file.id} style={styles.fileItem}>
              <View style={styles.fileInfo}>
                <Text style={styles.fileIcon}>📄</Text>
                <View style={styles.fileDetails}>
                  <Text style={styles.fileName}>{file.name}</Text>
                  <Text style={styles.fileSize}>
                    {file.size
                      ? `${(file.size / 1024 / 1024).toFixed(2)} MB`
                      : "Unknown size"}
                  </Text>
                </View>
              </View>
              <TouchableOpacity
                style={styles.removeButton}
                onPress={() => removeFile(file.id)}
              >
                <Text style={styles.removeButtonText}>✕</Text>
              </TouchableOpacity>
            </View>
          ))}
        </View>
      )}

      {/* Upload Button */}
      <View style={styles.actionContainer}>
        <TouchableOpacity
          style={[
            styles.submitButton,
            (selectedFiles.length === 0 || !formData.title.trim()) && styles.submitButtonDisabled,
          ]}
          onPress={uploadCourseMaterials}
          disabled={uploading || selectedFiles.length === 0 || !formData.title.trim()}
        >
          {uploading ? (
            <ActivityIndicator color="#FFFFFF" size="small" />
          ) : (
            <Text style={styles.submitButtonText}>
              Upload Course Materials
            </Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.cancelButton}
          onPress={() => navigation.goBack()}
          disabled={uploading}
        >
          <Text style={styles.cancelButtonText}>Cancel</Text>
        </TouchableOpacity>
      </View>

      {/* Help Text */}
      <View style={styles.helpContainer}>
        <Text style={styles.helpTitle}>Tips:</Text>
        <Text style={styles.helpText}>
          • Enable RAG to make materials searchable{"\n"}
          • Auto-extract questions will create practice questions{"\n"}
          • Maximum file size: 50MB per file{"\n"}
          • Supported formats: PDF, Word, PowerPoint, Text
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#f5f5f5",
  },
  header: {
    padding: 20,
    backgroundColor: "#fff",
    borderBottomWidth: 1,
    borderBottomColor: "#e0e0e0",
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#333",
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: "#666",
    lineHeight: 22,
  },
  formContainer: {
    backgroundColor: "#fff",
    margin: 16,
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
    marginBottom: 12,
  },
  input: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    marginBottom: 12,
    backgroundColor: "#fff",
  },
  textArea: {
    height: 80,
    textAlignVertical: "top",
  },
  pickerContainer: {
    marginBottom: 16,
  },
  pickerLabel: {
    fontSize: 16,
    fontWeight: "500",
    color: "#333",
    marginBottom: 8,
  },
  pickerButtons: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  pickerButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: "#ddd",
    backgroundColor: "#fff",
  },
  pickerButtonActive: {
    backgroundColor: "#007bff",
    borderColor: "#007bff",
  },
  pickerButtonText: {
    fontSize: 14,
    color: "#333",
  },
  pickerButtonTextActive: {
    color: "#fff",
  },
  optionsContainer: {
    marginTop: 16,
  },
  switchContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 8,
  },
  switchLabel: {
    fontSize: 16,
    color: "#333",
    flex: 1,
  },
  uploadSection: {
    backgroundColor: "#fff",
    margin: 16,
    marginTop: 0,
    padding: 16,
    borderRadius: 12,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  uploadButton: {
    flexDirection: "row",
    alignItems: "center",
    padding: 16,
    borderWidth: 2,
    borderColor: "#007bff",
    borderStyle: "dashed",
    borderRadius: 12,
    backgroundColor: "#f8f9ff",
  },
  uploadButtonIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  uploadButtonContent: {
    flex: 1,
  },
  uploadButtonTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#007bff",
    marginBottom: 4,
  },
  uploadButtonSubtitle: {
    fontSize: 14,
    color: "#666",
  },
  selectedFiles: {
    backgroundColor: "#fff",
    margin: 16,
    marginTop: 0,
    padding: 16,
    borderRadius: 12,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  fileItem: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: "#eee",
  },
  fileInfo: {
    flexDirection: "row",
    alignItems: "center",
    flex: 1,
  },
  fileIcon: {
    fontSize: 20,
    marginRight: 12,
  },
  fileDetails: {
    flex: 1,
  },
  fileName: {
    fontSize: 14,
    fontWeight: "500",
    color: "#333",
  },
  fileSize: {
    fontSize: 12,
    color: "#666",
    marginTop: 2,
  },
  removeButton: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: "#ff4444",
    alignItems: "center",
    justifyContent: "center",
  },
  removeButtonText: {
    color: "#fff",
    fontSize: 12,
    fontWeight: "bold",
  },
  actionContainer: {
    padding: 16,
  },
  submitButton: {
    backgroundColor: "#007bff",
    padding: 16,
    borderRadius: 12,
    alignItems: "center",
    marginBottom: 12,
  },
  submitButtonDisabled: {
    backgroundColor: "#ccc",
  },
  submitButtonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
  cancelButton: {
    backgroundColor: "#f8f9fa",
    padding: 16,
    borderRadius: 12,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#ddd",
  },
  cancelButtonText: {
    color: "#666",
    fontSize: 16,
    fontWeight: "600",
  },
  helpContainer: {
    backgroundColor: "#fff",
    margin: 16,
    marginTop: 0,
    padding: 16,
    borderRadius: 12,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  helpTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#333",
    marginBottom: 8,
  },
  helpText: {
    fontSize: 14,
    color: "#666",
    lineHeight: 20,
  },
});

export default CourseMaterialsUploadScreen;
