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
} from "react-native";
import { useSelector, useDispatch } from "react-redux";
import { logout } from "../store/authSlice";
import * as DocumentPicker from "expo-document-picker";
import * as ImagePicker from "expo-image-picker";
import uploadService from "../api/uploadService";
import apiClient from "../api/client";

const UploadScreen = ({ navigation }) => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [subject, setSubject] = useState("");
  const [topic, setTopic] = useState("");
  const [description, setDescription] = useState("");
  const user = useSelector((state) => state.auth.user);
  const token = useSelector((state) => state.auth.token);
  const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);
  const dispatch = useDispatch();

  const pickDocument = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: [
          "application/pdf",
          "text/plain",
          "application/msword",
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ],
        copyToCacheDirectory: true,
        multiple: false,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        const file = result.assets[0];
        setSelectedFiles((prev) => [
          ...prev,
          {
            ...file,
            type: "document",
            id: Date.now() + Math.random(),
          },
        ]);
      }
    } catch (error) {
      Alert.alert("Error", "Failed to pick document");
    }
  };

  const pickImage = async () => {
    try {
      const permissionResult =
        await ImagePicker.requestMediaLibraryPermissionsAsync();

      if (!permissionResult.granted) {
        Alert.alert(
          "Permission Required",
          "Please grant permission to access your photo library"
        );
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        const image = result.assets[0];
        setSelectedFiles((prev) => [
          ...prev,
          {
            ...image,
            name: `image_${Date.now()}.jpg`,
            type: "image",
            id: Date.now() + Math.random(),
          },
        ]);
      }
    } catch (error) {
      Alert.alert("Error", "Failed to pick image");
    }
  };

  const takePhoto = async () => {
    try {
      const permissionResult =
        await ImagePicker.requestCameraPermissionsAsync();

      if (!permissionResult.granted) {
        Alert.alert(
          "Permission Required",
          "Please grant permission to access your camera"
        );
        return;
      }

      const result = await ImagePicker.launchCameraAsync({
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.8,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        const image = result.assets[0];
        setSelectedFiles((prev) => [
          ...prev,
          {
            ...image,
            name: `photo_${Date.now()}.jpg`,
            type: "image",
            id: Date.now() + Math.random(),
          },
        ]);
      }
    } catch (error) {
      Alert.alert("Error", "Failed to take photo");
    }
  };

  const removeFile = (fileId) => {
    setSelectedFiles((prev) => prev.filter((file) => file.id !== fileId));
  };

  const uploadFiles = async () => {
    if (selectedFiles.length === 0) {
      Alert.alert("No Files", "Please select at least one file to upload");
      return;
    }

    // Check if user is logged in with proper token access
    if (!isAuthenticated || !token) {
      Alert.alert(
        "Login Required",
        "Please log in to upload files.\n\nYou need to be authenticated to upload and process questions.",
        [
          {
            text: "Logout & Login Again",
            onPress: () => {
              dispatch(logout());
              // Navigation will be handled by auth state change
            },
          },
          { text: "Cancel", style: "cancel" },
        ]
      );
      return;
    }

    setUploading(true);

    try {
      // Prepare file objects for upload
      const files = selectedFiles.map((file) => ({
        uri: file.uri,
        type: file.type === "image" 
          ? file.mimeType || "image/jpeg" 
          : file.mimeType || "application/pdf",
        name: file.name,
      }));

      // Upload as course materials with question extraction enabled
      const uploadData = {
        subject_id: 1, // TODO: Allow user to select subject
        title: subject || "Uploaded Questions",
        description: description || "Questions uploaded from mobile app",
        material_type: "past_questions",
        tags: topic ? `mobile_upload,${topic}` : "mobile_upload",
        enable_rag: true,
        auto_extract_questions: true,
        files: files,
      };

      console.log("Uploading files with data:", uploadData);

      const result = await uploadService.uploadCourseMaterials(uploadData);

      console.log("Upload result:", result);

      Alert.alert(
        "Upload Successful!",
        `Successfully uploaded ${result.uploaded_files.length} file(s). They will be processed and added to your question bank.`,
        [
          {
            text: "OK",
            onPress: () => {
              setSelectedFiles([]);
              setSubject("");
              setTopic("");
              setDescription("");
              navigation.goBack();
            },
          },
        ]
      );
    } catch (error) {
      console.error("Upload error:", error);
      Alert.alert(
        "Upload Failed", 
        error.response?.data?.detail || "Failed to upload files. Please try again."
      );
    } finally {
      setUploading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Upload Past Questions</Text>
        <Text style={styles.subtitle}>
          Upload documents, images, or photos of past questions to build your
          question bank
        </Text>
      </View>

      {/* Metadata Input */}
      <View style={styles.metadataContainer}>
        <Text style={styles.sectionTitle}>Question Details (Optional)</Text>

        <TextInput
          style={styles.input}
          placeholder="Subject (e.g., Mathematics, Physics)"
          value={subject}
          onChangeText={setSubject}
        />

        <TextInput
          style={styles.input}
          placeholder="Topic (e.g., Calculus, Mechanics)"
          value={topic}
          onChangeText={setTopic}
        />

        <TextInput
          style={[styles.input, styles.textArea]}
          placeholder="Description or notes about these questions..."
          value={description}
          onChangeText={setDescription}
          multiline
          numberOfLines={3}
        />
      </View>

      {/* Upload Options */}
      <View style={styles.uploadOptions}>
        <Text style={styles.sectionTitle}>Choose Upload Method</Text>

        <TouchableOpacity style={styles.uploadButton} onPress={pickDocument}>
          <Text style={styles.uploadButtonIcon}>📄</Text>
          <View style={styles.uploadButtonContent}>
            <Text style={styles.uploadButtonTitle}>Upload Document</Text>
            <Text style={styles.uploadButtonSubtitle}>
              PDF, Word, or Text files
            </Text>
          </View>
        </TouchableOpacity>

        <TouchableOpacity style={styles.uploadButton} onPress={pickImage}>
          <Text style={styles.uploadButtonIcon}>🖼️</Text>
          <View style={styles.uploadButtonContent}>
            <Text style={styles.uploadButtonTitle}>Choose from Gallery</Text>
            <Text style={styles.uploadButtonSubtitle}>
              Select images from your device
            </Text>
          </View>
        </TouchableOpacity>

        <TouchableOpacity style={styles.uploadButton} onPress={takePhoto}>
          <Text style={styles.uploadButtonIcon}>📸</Text>
          <View style={styles.uploadButtonContent}>
            <Text style={styles.uploadButtonTitle}>Take Photo</Text>
            <Text style={styles.uploadButtonSubtitle}>
              Capture questions with camera
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
                <Text style={styles.fileIcon}>
                  {file.type === "image" ? "🖼️" : "📄"}
                </Text>
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
            selectedFiles.length === 0 && styles.submitButtonDisabled,
          ]}
          onPress={uploadFiles}
          disabled={uploading || selectedFiles.length === 0}
        >
          {uploading ? (
            <ActivityIndicator color="#FFFFFF" size="small" />
          ) : (
            <Text style={styles.submitButtonText}>
              Upload{" "}
              {selectedFiles.length > 0
                ? `${selectedFiles.length} File(s)`
                : "Files"}
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
        <Text style={styles.helpTitle}>💡 Tips for Best Results</Text>
        <Text style={styles.helpText}>
          • Ensure images are clear and well-lit
        </Text>
        <Text style={styles.helpText}>
          • Upload high-quality scans when possible
        </Text>
        <Text style={styles.helpText}>
          • Include subject and topic for better organization
        </Text>
        <Text style={styles.helpText}>
          • Supported formats: PDF, Word, JPG, PNG
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F8F9FA",
  },
  header: {
    padding: 20,
    backgroundColor: "#FFFFFF",
    borderBottomWidth: 1,
    borderBottomColor: "#E1E8ED",
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#2C3E50",
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: "#7F8C8D",
    lineHeight: 22,
  },
  metadataContainer: {
    padding: 20,
    backgroundColor: "#FFFFFF",
    marginTop: 10,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "600",
    color: "#2C3E50",
    marginBottom: 15,
  },
  input: {
    borderWidth: 1,
    borderColor: "#E1E8ED",
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: "#FFFFFF",
    marginBottom: 12,
  },
  textArea: {
    height: 80,
    textAlignVertical: "top",
  },
  uploadOptions: {
    padding: 20,
    backgroundColor: "#FFFFFF",
    marginTop: 10,
  },
  uploadButton: {
    flexDirection: "row",
    alignItems: "center",
    padding: 16,
    backgroundColor: "#F8F9FA",
    borderRadius: 12,
    borderWidth: 2,
    borderColor: "#E1E8ED",
    borderStyle: "dashed",
    marginBottom: 12,
  },
  uploadButtonIcon: {
    fontSize: 24,
    marginRight: 16,
  },
  uploadButtonContent: {
    flex: 1,
  },
  uploadButtonTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#2C3E50",
    marginBottom: 4,
  },
  uploadButtonSubtitle: {
    fontSize: 14,
    color: "#7F8C8D",
  },
  selectedFiles: {
    padding: 20,
    backgroundColor: "#FFFFFF",
    marginTop: 10,
  },
  fileItem: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    padding: 12,
    backgroundColor: "#F8F9FA",
    borderRadius: 8,
    marginBottom: 8,
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
    color: "#2C3E50",
    marginBottom: 2,
  },
  fileSize: {
    fontSize: 12,
    color: "#7F8C8D",
  },
  removeButton: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: "#E74C3C",
    justifyContent: "center",
    alignItems: "center",
  },
  removeButtonText: {
    color: "#FFFFFF",
    fontSize: 12,
    fontWeight: "bold",
  },
  actionContainer: {
    padding: 20,
  },
  submitButton: {
    backgroundColor: "#3498DB",
    padding: 16,
    borderRadius: 8,
    alignItems: "center",
    marginBottom: 12,
  },
  submitButtonDisabled: {
    backgroundColor: "#BDC3C7",
  },
  submitButtonText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "600",
  },
  cancelButton: {
    backgroundColor: "transparent",
    padding: 16,
    borderRadius: 8,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#BDC3C7",
  },
  cancelButtonText: {
    color: "#7F8C8D",
    fontSize: 16,
    fontWeight: "500",
  },
  helpContainer: {
    padding: 20,
    backgroundColor: "#E8F4FD",
    marginTop: 10,
    marginBottom: 20,
  },
  helpTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#2C3E50",
    marginBottom: 12,
  },
  helpText: {
    fontSize: 14,
    color: "#7F8C8D",
    marginBottom: 6,
    lineHeight: 20,
  },
});

export default UploadScreen;
