import React from "react";
import { createStackNavigator } from "@react-navigation/stack";
import { MaterialIcons } from "@expo/vector-icons";

// Admin Screens
import AdminDashboardScreen from "../screens/AdminDashboardScreen";
import UserManagementScreen from "../screens/UserManagementScreen";
import QuestionManagementScreen from "../screens/QuestionManagementScreen";
import AdminAnalyticsScreen from "../screens/AdminAnalyticsScreen";
import DatabaseQueryScreen from "../screens/DatabaseQueryScreen";

// Placeholder screens for remaining admin features
import UploadManagementScreen from "../screens/UploadManagementScreen";
import ContentReviewScreen from "../screens/ContentReviewScreen";
import SystemSettingsScreen from "../screens/SystemSettingsScreen";
import SystemLogsScreen from "../screens/SystemLogsScreen";

const Stack = createStackNavigator();

const AdminStackNavigator = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        cardStyle: { backgroundColor: "#f5f5f5" },
      }}
    >
      <Stack.Screen
        name="AdminDashboard"
        component={AdminDashboardScreen}
        options={{
          title: "Admin Dashboard",
          headerShown: false,
        }}
      />
      <Stack.Screen
        name="UserManagement"
        component={UserManagementScreen}
        options={{
          title: "User Management",
          headerShown: false,
        }}
      />
      <Stack.Screen
        name="QuestionManagement"
        component={QuestionManagementScreen}
        options={{
          title: "Question Management",
          headerShown: false,
        }}
      />
      <Stack.Screen
        name="AdminAnalytics"
        component={AdminAnalyticsScreen}
        options={{
          title: "Analytics & Reports",
          headerShown: false,
        }}
      />
      <Stack.Screen
        name="DatabaseQuery"
        component={DatabaseQueryScreen}
        options={{
          title: "Database Query",
          headerShown: false,
        }}
      />
      <Stack.Screen
        name="UploadManagement"
        component={UploadManagementScreen}
        options={{
          title: "Upload Management",
          headerShown: false,
        }}
      />
      <Stack.Screen
        name="ContentReview"
        component={ContentReviewScreen}
        options={{
          title: "Content Review",
          headerShown: false,
        }}
      />
      <Stack.Screen
        name="SystemSettings"
        component={SystemSettingsScreen}
        options={{
          title: "System Settings",
          headerShown: false,
        }}
      />
      <Stack.Screen
        name="SystemLogs"
        component={SystemLogsScreen}
        options={{
          title: "System Logs",
          headerShown: false,
        }}
      />
    </Stack.Navigator>
  );
};

export default AdminStackNavigator;
