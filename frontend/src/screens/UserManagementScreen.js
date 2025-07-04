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
} from "react-native";
import { useSelector } from "react-redux";
import { MaterialIcons } from "@expo/vector-icons";

const UserManagementScreen = ({ navigation }) => {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [showAddUserModal, setShowAddUserModal] = useState(false);
  const [showUserDetailModal, setShowUserDetailModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [filterActive, setFilterActive] = useState(null);

  const [newUser, setNewUser] = useState({
    username: "",
    email: "",
    password: "",
    isActive: true,
    role: "user",
  });

  const token = useSelector((state) => state.auth.token);

  useEffect(() => {
    loadUsers();
  }, []);

  useEffect(() => {
    filterUsers();
  }, [searchQuery, filterActive, users]);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await fetch("http://172.16.17.124:8000/api/v1/admin/users", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch users");
      }

      const data = await response.json();
      setUsers(data);
      setFilteredUsers(data);
    } catch (error) {
      console.error("Error loading users:", error);
      Alert.alert("Error", "Failed to load users. Check your admin privileges.");
      // Fallback to empty array
      setUsers([]);
      setFilteredUsers([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const filterUsers = () => {
    let filtered = users;

    if (searchQuery) {
      filtered = filtered.filter(
        (user) =>
          (user.username && user.username.toLowerCase().includes(searchQuery.toLowerCase())) ||
          user.email.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (filterActive !== null) {
      filtered = filtered.filter((user) => user.is_active === filterActive);
    }

    setFilteredUsers(filtered);
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadUsers();
  };

  const handleAddUser = async () => {
    try {
      if (!newUser.username || !newUser.email || !newUser.password) {
        Alert.alert("Error", "Please fill in all required fields");
        return;
      }

      // TODO: Implement API call to create user
      Alert.alert("Success", "User created successfully");
      setShowAddUserModal(false);
      setNewUser({
        username: "",
        email: "",
        password: "",
        isActive: true,
        role: "user",
      });
      loadUsers();
    } catch (error) {
      console.error("Error creating user:", error);
      Alert.alert("Error", "Failed to create user");
    }
  };

  const handleToggleUserStatus = async (userId, currentStatus) => {
    try {
      // TODO: Implement API call to toggle user status
      Alert.alert(
        "Confirm",
        `Are you sure you want to ${currentStatus ? "deactivate" : "activate"} this user?`,
        [
          { text: "Cancel", style: "cancel" },
          {
            text: "Confirm",
            onPress: () => {
              setUsers(users.map(user => 
                user.id === userId 
                  ? { ...user, isActive: !currentStatus }
                  : user
              ));
              Alert.alert("Success", `User ${currentStatus ? "deactivated" : "activated"} successfully`);
            },
          },
        ]
      );
    } catch (error) {
      console.error("Error toggling user status:", error);
      Alert.alert("Error", "Failed to update user status");
    }
  };

  const handleDeleteUser = async (userId) => {
    try {
      Alert.alert(
        "Confirm Delete",
        "Are you sure you want to delete this user? This action cannot be undone.",
        [
          { text: "Cancel", style: "cancel" },
          {
            text: "Delete",
            style: "destructive",
            onPress: () => {
              setUsers(users.filter(user => user.id !== userId));
              Alert.alert("Success", "User deleted successfully");
            },
          },
        ]
      );
    } catch (error) {
      console.error("Error deleting user:", error);
      Alert.alert("Error", "Failed to delete user");
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getRoleColor = (role) => {
    switch (role) {
      case "admin":
        return "#F44336";
      case "moderator":
        return "#FF9800";
      case "user":
        return "#4CAF50";
      default:
        return "#9E9E9E";
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007bff" />
        <Text style={styles.loadingText}>Loading users...</Text>
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
        <Text style={styles.title}>User Management</Text>
        <TouchableOpacity
          style={styles.addButton}
          onPress={() => setShowAddUserModal(true)}
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
            placeholder="Search users..."
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
        </View>
        <View style={styles.filterContainer}>
          <TouchableOpacity
            style={[
              styles.filterButton,
              filterActive === null && styles.activeFilter,
            ]}
            onPress={() => setFilterActive(null)}
          >
            <Text style={styles.filterText}>All</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[
              styles.filterButton,
              filterActive === true && styles.activeFilter,
            ]}
            onPress={() => setFilterActive(true)}
          >
            <Text style={styles.filterText}>Active</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[
              styles.filterButton,
              filterActive === false && styles.activeFilter,
            ]}
            onPress={() => setFilterActive(false)}
          >
            <Text style={styles.filterText}>Inactive</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* User List */}
      <ScrollView
        style={styles.userList}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {filteredUsers.map((user) => (
          <TouchableOpacity
            key={user.id}
            style={styles.userCard}
            onPress={() => {
              setSelectedUser(user);
              setShowUserDetailModal(true);
            }}
          >
            <View style={styles.userInfo}>
              <View style={styles.userHeader}>
                <Text style={styles.username}>{user.username}</Text>
                <View style={styles.userBadges}>
                  <View style={[styles.roleBadge, { backgroundColor: getRoleColor(user.role) }]}>
                    <Text style={styles.roleText}>{user.role}</Text>
                  </View>
                  <View style={[
                    styles.statusBadge,
                    { backgroundColor: user.isActive ? "#4CAF50" : "#F44336" }
                  ]}>
                    <Text style={styles.statusText}>
                      {user.isActive ? "Active" : "Inactive"}
                    </Text>
                  </View>
                </View>
              </View>
              <Text style={styles.userEmail}>{user.email}</Text>
              <View style={styles.userStats}>
                <Text style={styles.statText}>
                  Questions: {user.totalQuestions} | Uploads: {user.totalUploads}
                </Text>
                <Text style={styles.dateText}>
                  Last login: {formatDate(user.lastLogin)}
                </Text>
              </View>
            </View>
            <View style={styles.userActions}>
              <TouchableOpacity
                style={styles.actionButton}
                onPress={() => handleToggleUserStatus(user.id, user.isActive)}
              >
                <MaterialIcons 
                  name={user.isActive ? "block" : "check-circle"} 
                  size={20} 
                  color={user.isActive ? "#F44336" : "#4CAF50"} 
                />
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.actionButton}
                onPress={() => handleDeleteUser(user.id)}
              >
                <MaterialIcons name="delete" size={20} color="#F44336" />
              </TouchableOpacity>
            </View>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Add User Modal */}
      <Modal
        visible={showAddUserModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowAddUserModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Add New User</Text>
              <TouchableOpacity
                onPress={() => setShowAddUserModal(false)}
              >
                <MaterialIcons name="close" size={24} color="#666" />
              </TouchableOpacity>
            </View>
            
            <ScrollView style={styles.modalForm}>
              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Username *</Text>
                <TextInput
                  style={styles.textInput}
                  value={newUser.username}
                  onChangeText={(text) => setNewUser({...newUser, username: text})}
                  placeholder="Enter username"
                />
              </View>
              
              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Email *</Text>
                <TextInput
                  style={styles.textInput}
                  value={newUser.email}
                  onChangeText={(text) => setNewUser({...newUser, email: text})}
                  placeholder="Enter email"
                  keyboardType="email-address"
                />
              </View>
              
              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Password *</Text>
                <TextInput
                  style={styles.textInput}
                  value={newUser.password}
                  onChangeText={(text) => setNewUser({...newUser, password: text})}
                  placeholder="Enter password"
                  secureTextEntry
                />
              </View>
              
              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Role</Text>
                <View style={styles.roleSelector}>
                  {["user", "moderator", "admin"].map((role) => (
                    <TouchableOpacity
                      key={role}
                      style={[
                        styles.roleOption,
                        newUser.role === role && styles.selectedRole,
                      ]}
                      onPress={() => setNewUser({...newUser, role})}
                    >
                      <Text style={styles.roleOptionText}>{role}</Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>
              
              <View style={styles.switchGroup}>
                <Text style={styles.inputLabel}>Active</Text>
                <Switch
                  value={newUser.isActive}
                  onValueChange={(value) => setNewUser({...newUser, isActive: value})}
                />
              </View>
            </ScrollView>
            
            <View style={styles.modalActions}>
              <TouchableOpacity
                style={styles.cancelButton}
                onPress={() => setShowAddUserModal(false)}
              >
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.confirmButton}
                onPress={handleAddUser}
              >
                <Text style={styles.confirmButtonText}>Add User</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* User Detail Modal */}
      <Modal
        visible={showUserDetailModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowUserDetailModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>User Details</Text>
              <TouchableOpacity
                onPress={() => setShowUserDetailModal(false)}
              >
                <MaterialIcons name="close" size={24} color="#666" />
              </TouchableOpacity>
            </View>
            
            {selectedUser && (
              <ScrollView style={styles.detailContent}>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Username:</Text>
                  <Text style={styles.detailValue}>{selectedUser.username}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Email:</Text>
                  <Text style={styles.detailValue}>{selectedUser.email}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Role:</Text>
                  <Text style={[styles.detailValue, { color: getRoleColor(selectedUser.role) }]}>
                    {selectedUser.role}
                  </Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Status:</Text>
                  <Text style={[
                    styles.detailValue,
                    { color: selectedUser.isActive ? "#4CAF50" : "#F44336" }
                  ]}>
                    {selectedUser.isActive ? "Active" : "Inactive"}
                  </Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Total Questions:</Text>
                  <Text style={styles.detailValue}>{selectedUser.totalQuestions}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Total Uploads:</Text>
                  <Text style={styles.detailValue}>{selectedUser.totalUploads}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Created At:</Text>
                  <Text style={styles.detailValue}>{formatDate(selectedUser.createdAt)}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Last Login:</Text>
                  <Text style={styles.detailValue}>{formatDate(selectedUser.lastLogin)}</Text>
                </View>
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
    flexDirection: "row",
    gap: 8,
  },
  filterButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: "#f5f5f5",
  },
  activeFilter: {
    backgroundColor: "#007bff",
  },
  filterText: {
    color: "#666",
    fontSize: 14,
  },
  userList: {
    flex: 1,
  },
  userCard: {
    backgroundColor: "#fff",
    margin: 8,
    marginBottom: 0,
    padding: 16,
    borderRadius: 8,
    flexDirection: "row",
    alignItems: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  userInfo: {
    flex: 1,
  },
  userHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 4,
  },
  username: {
    fontSize: 16,
    fontWeight: "600",
    color: "#333",
  },
  userBadges: {
    flexDirection: "row",
    gap: 8,
  },
  roleBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 12,
  },
  roleText: {
    color: "#fff",
    fontSize: 10,
    fontWeight: "bold",
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 12,
  },
  statusText: {
    color: "#fff",
    fontSize: 10,
    fontWeight: "bold",
  },
  userEmail: {
    fontSize: 14,
    color: "#666",
    marginBottom: 8,
  },
  userStats: {
    gap: 4,
  },
  statText: {
    fontSize: 12,
    color: "#666",
  },
  dateText: {
    fontSize: 12,
    color: "#999",
  },
  userActions: {
    flexDirection: "row",
    gap: 12,
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
  },
  roleSelector: {
    flexDirection: "row",
    gap: 8,
  },
  roleOption: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: "#f5f5f5",
    borderWidth: 1,
    borderColor: "#ddd",
  },
  selectedRole: {
    backgroundColor: "#007bff",
    borderColor: "#007bff",
  },
  roleOptionText: {
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
  },
  detailValue: {
    fontSize: 14,
    color: "#333",
  },
});

export default UserManagementScreen;
