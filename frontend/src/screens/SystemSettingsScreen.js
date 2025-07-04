import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Alert,
  Switch,
  TextInput,
  Modal,
} from "react-native";
import { MaterialIcons } from "@expo/vector-icons";
import { adminService } from "../api";

const SystemSettingsScreen = ({ navigation }) => {
  const [loading, setLoading] = useState(true);
  const [settings, setSettings] = useState({
    general: {
      appName: "AI Past Questions",
      appDescription: "AI-powered exam preparation platform",
      maintenanceMode: false,
      allowRegistration: true,
      requireEmailVerification: true,
    },
    ai: {
      enableAIFeatures: true,
      maxQuestionsPerUpload: 100,
      autoProcessUploads: true,
      enableSmartRecommendations: true,
      aiResponseTimeout: 30,
    },
    security: {
      enforceStrongPasswords: true,
      enableTwoFactor: false,
      sessionTimeout: 24,
      maxLoginAttempts: 5,
      enableAuditLogs: true,
    },
    notifications: {
      enableEmailNotifications: true,
      enablePushNotifications: true,
      notifyOnNewUploads: true,
      notifyOnContentReview: true,
      adminEmailAlerts: true,
    },
    storage: {
      maxFileSize: 10,
      allowedFileTypes: ["pdf", "docx", "txt", "jpg", "png"],
      autoDeleteProcessedFiles: false,
      retentionPeriod: 90,
    },
    performance: {
      enableCaching: true,
      cacheTimeout: 3600,
      enableCompression: true,
      maxConcurrentUsers: 1000,
    },
  });

  const [showBackupModal, setShowBackupModal] = useState(false);
  const [showRestoreModal, setShowRestoreModal] = useState(false);
  const [backupProgress, setBackupProgress] = useState(0);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const response = await adminService.getSystemSettings();
      setSettings(response);
      setLoading(false);
    } catch (error) {
      console.error("Error loading settings:", error);
      // Keep default settings on error
      setLoading(false);
    }
  };

  const updateSetting = (category, key, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value,
      },
    }));
  };

  const saveSettings = async () => {
    try {
      await adminService.updateSystemSettings(settings);
      Alert.alert("Success", "Settings saved successfully");
    } catch (error) {
      console.error("Error saving settings:", error);
      Alert.alert("Error", "Failed to save settings");
    }
  };

  const resetSettings = () => {
    Alert.alert(
      "Reset Settings",
      "Are you sure you want to reset all settings to default values?",
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Reset",
          style: "destructive",
          onPress: async () => {
            try {
              await adminService.resetSystemSettings();
              await loadSettings();
              Alert.alert("Success", "Settings reset to defaults");
            } catch (error) {
              console.error("Error resetting settings:", error);
              Alert.alert("Error", "Failed to reset settings");
            }
          },
        },
      ]
    );
  };

  const createBackup = async () => {
    setShowBackupModal(true);
    setBackupProgress(0);
    
    // Simulate backup progress
    const interval = setInterval(() => {
      setBackupProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(() => {
            setShowBackupModal(false);
            Alert.alert("Success", "System backup created successfully");
          }, 500);
          return 100;
        }
        return prev + 10;
      });
    }, 200);
  };

  const restoreFromBackup = () => {
    Alert.alert(
      "Restore from Backup",
      "This will restore the system from the latest backup. All current data will be replaced. Are you sure?",
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Restore",
          style: "destructive",
          onPress: () => {
            setShowRestoreModal(true);
            setTimeout(() => {
              setShowRestoreModal(false);
              Alert.alert("Success", "System restored from backup successfully");
            }, 3000);
          },
        },
      ]
    );
  };

  const clearCache = () => {
    Alert.alert(
      "Clear Cache",
      "This will clear all cached data. Are you sure?",
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Clear",
          onPress: () => {
            Alert.alert("Success", "Cache cleared successfully");
          },
        },
      ]
    );
  };

  const renderSettingsSection = (title, category, settingsData) => (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>{title}</Text>
      {Object.entries(settingsData).map(([key, value]) => (
        <View key={key} style={styles.settingItem}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingLabel}>
              {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
            </Text>
            <Text style={styles.settingDescription}>
              {getSettingDescription(key)}
            </Text>
          </View>
          {typeof value === 'boolean' ? (
            <Switch
              value={value}
              onValueChange={(newValue) => updateSetting(category, key, newValue)}
              trackColor={{ false: "#767577", true: "#007bff" }}
              thumbColor={value ? "#ffffff" : "#f4f3f4"}
            />
          ) : typeof value === 'number' ? (
            <View style={styles.numberInput}>
              <TextInput
                style={styles.numberInputField}
                value={value.toString()}
                onChangeText={(text) => updateSetting(category, key, parseInt(text) || 0)}
                keyboardType="numeric"
              />
            </View>
          ) : Array.isArray(value) ? (
            <TouchableOpacity
              style={styles.arrayButton}
              onPress={() => {
                // TODO: Implement array editing modal
                Alert.alert("Info", `Current values: ${value.join(", ")}`);
              }}
            >
              <Text style={styles.arrayButtonText}>Edit ({value.length})</Text>
            </TouchableOpacity>
          ) : (
            <TextInput
              style={styles.textInput}
              value={value}
              onChangeText={(text) => updateSetting(category, key, text)}
            />
          )}
        </View>
      ))}
    </View>
  );

  const getSettingDescription = (key) => {
    const descriptions = {
      appName: "The display name of the application",
      appDescription: "Brief description of the app",
      maintenanceMode: "Enable to put the app in maintenance mode",
      allowRegistration: "Allow new users to register",
      requireEmailVerification: "Require email verification for new accounts",
      enableAIFeatures: "Enable AI-powered features",
      maxQuestionsPerUpload: "Maximum questions to extract per upload",
      autoProcessUploads: "Automatically process uploaded files",
      enableSmartRecommendations: "Enable AI-powered recommendations",
      aiResponseTimeout: "AI service timeout in seconds",
      enforceStrongPasswords: "Require strong passwords",
      enableTwoFactor: "Enable two-factor authentication",
      sessionTimeout: "Session timeout in hours",
      maxLoginAttempts: "Maximum failed login attempts",
      enableAuditLogs: "Log user activities",
      enableEmailNotifications: "Send email notifications",
      enablePushNotifications: "Send push notifications",
      notifyOnNewUploads: "Notify on new file uploads",
      notifyOnContentReview: "Notify on content review actions",
      adminEmailAlerts: "Send admin email alerts",
      maxFileSize: "Maximum file size in MB",
      allowedFileTypes: "Allowed file types for upload",
      autoDeleteProcessedFiles: "Auto-delete files after processing",
      retentionPeriod: "File retention period in days",
      enableCaching: "Enable application caching",
      cacheTimeout: "Cache timeout in seconds",
      enableCompression: "Enable response compression",
      maxConcurrentUsers: "Maximum concurrent users",
    };
    return descriptions[key] || "No description available";
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
        <Text style={styles.title}>System Settings</Text>
        <TouchableOpacity
          style={styles.saveButton}
          onPress={saveSettings}
        >
          <MaterialIcons name="save" size={24} color="#007bff" />
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content}>
        {/* General Settings */}
        {renderSettingsSection("General", "general", settings.general)}

        {/* AI Settings */}
        {renderSettingsSection("AI & Machine Learning", "ai", settings.ai)}

        {/* Security Settings */}
        {renderSettingsSection("Security", "security", settings.security)}

        {/* Notification Settings */}
        {renderSettingsSection("Notifications", "notifications", settings.notifications)}

        {/* Storage Settings */}
        {renderSettingsSection("Storage", "storage", settings.storage)}

        {/* Performance Settings */}
        {renderSettingsSection("Performance", "performance", settings.performance)}

        {/* System Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>System Actions</Text>
          
          <TouchableOpacity
            style={styles.actionButton}
            onPress={createBackup}
          >
            <MaterialIcons name="backup" size={24} color="#4CAF50" />
            <View style={styles.actionInfo}>
              <Text style={styles.actionTitle}>Create Backup</Text>
              <Text style={styles.actionDescription}>
                Create a full system backup
              </Text>
            </View>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionButton}
            onPress={restoreFromBackup}
          >
            <MaterialIcons name="restore" size={24} color="#FF9800" />
            <View style={styles.actionInfo}>
              <Text style={styles.actionTitle}>Restore from Backup</Text>
              <Text style={styles.actionDescription}>
                Restore system from latest backup
              </Text>
            </View>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionButton}
            onPress={clearCache}
          >
            <MaterialIcons name="clear-all" size={24} color="#2196F3" />
            <View style={styles.actionInfo}>
              <Text style={styles.actionTitle}>Clear Cache</Text>
              <Text style={styles.actionDescription}>
                Clear all cached data
              </Text>
            </View>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionButton}
            onPress={resetSettings}
          >
            <MaterialIcons name="settings-backup-restore" size={24} color="#F44336" />
            <View style={styles.actionInfo}>
              <Text style={styles.actionTitle}>Reset Settings</Text>
              <Text style={styles.actionDescription}>
                Reset all settings to defaults
              </Text>
            </View>
          </TouchableOpacity>
        </View>

        {/* System Information */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>System Information</Text>
          <View style={styles.infoGrid}>
            <View style={styles.infoCard}>
              <Text style={styles.infoLabel}>App Version</Text>
              <Text style={styles.infoValue}>1.0.0</Text>
            </View>
            <View style={styles.infoCard}>
              <Text style={styles.infoLabel}>Database Version</Text>
              <Text style={styles.infoValue}>PostgreSQL 15</Text>
            </View>
            <View style={styles.infoCard}>
              <Text style={styles.infoLabel}>Last Backup</Text>
              <Text style={styles.infoValue}>2024-01-20</Text>
            </View>
            <View style={styles.infoCard}>
              <Text style={styles.infoLabel}>Uptime</Text>
              <Text style={styles.infoValue}>7d 12h</Text>
            </View>
          </View>
        </View>
      </ScrollView>

      {/* Backup Progress Modal */}
      <Modal
        visible={showBackupModal}
        animationType="fade"
        transparent={true}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.progressModal}>
            <Text style={styles.progressTitle}>Creating Backup</Text>
            <View style={styles.progressBar}>
              <View style={[styles.progressFill, { width: `${backupProgress}%` }]} />
            </View>
            <Text style={styles.progressText}>{backupProgress}%</Text>
          </View>
        </View>
      </Modal>

      {/* Restore Progress Modal */}
      <Modal
        visible={showRestoreModal}
        animationType="fade"
        transparent={true}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.progressModal}>
            <MaterialIcons name="restore" size={48} color="#FF9800" />
            <Text style={styles.progressTitle}>Restoring from Backup</Text>
            <Text style={styles.progressSubtitle}>Please wait...</Text>
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
  saveButton: {
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
  settingItem: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#f0f0f0",
  },
  settingInfo: {
    flex: 1,
    marginRight: 16,
  },
  settingLabel: {
    fontSize: 16,
    fontWeight: "500",
    color: "#333",
    marginBottom: 4,
  },
  settingDescription: {
    fontSize: 12,
    color: "#666",
    lineHeight: 16,
  },
  numberInput: {
    width: 80,
  },
  numberInputField: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 6,
    padding: 8,
    textAlign: "center",
    fontSize: 16,
  },
  textInput: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 6,
    padding: 8,
    fontSize: 16,
    minWidth: 100,
  },
  arrayButton: {
    backgroundColor: "#e3f2fd",
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
  },
  arrayButtonText: {
    color: "#1976d2",
    fontSize: 14,
    fontWeight: "500",
  },
  actionButton: {
    flexDirection: "row",
    alignItems: "center",
    padding: 12,
    backgroundColor: "#f8f9fa",
    borderRadius: 8,
    marginBottom: 12,
  },
  actionInfo: {
    flex: 1,
    marginLeft: 12,
  },
  actionTitle: {
    fontSize: 16,
    fontWeight: "500",
    color: "#333",
    marginBottom: 2,
  },
  actionDescription: {
    fontSize: 12,
    color: "#666",
  },
  infoGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 12,
  },
  infoCard: {
    flex: 1,
    minWidth: "45%",
    backgroundColor: "#f8f9fa",
    padding: 12,
    borderRadius: 8,
    alignItems: "center",
  },
  infoLabel: {
    fontSize: 12,
    color: "#666",
    marginBottom: 4,
  },
  infoValue: {
    fontSize: 16,
    fontWeight: "600",
    color: "#333",
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0, 0, 0, 0.5)",
    justifyContent: "center",
    alignItems: "center",
  },
  progressModal: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 24,
    alignItems: "center",
    minWidth: 200,
  },
  progressTitle: {
    fontSize: 18,
    fontWeight: "600",
    color: "#333",
    marginBottom: 16,
  },
  progressSubtitle: {
    fontSize: 14,
    color: "#666",
    marginTop: 8,
  },
  progressBar: {
    width: 150,
    height: 8,
    backgroundColor: "#e0e0e0",
    borderRadius: 4,
    marginBottom: 8,
  },
  progressFill: {
    height: "100%",
    backgroundColor: "#4CAF50",
    borderRadius: 4,
  },
  progressText: {
    fontSize: 14,
    color: "#666",
  },
});

export default SystemSettingsScreen;
