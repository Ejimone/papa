import React from 'react';
import { Text } from 'react-native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { useSelector } from 'react-redux';

import AIDashboardScreen from '../screens/AIDashboardScreen';
import PracticeStackNavigator from './PracticeStackNavigator';
import LearnStackNavigator from './LearnStackNavigator';
import SearchScreen from '../screens/SearchScreen';
import ProfileScreen from '../screens/ProfileScreen';
import AdminStackNavigator from './AdminStackNavigator';

const Tab = createBottomTabNavigator();

const MainTabNavigator = () => {
  const user = useSelector((state) => state.auth.user);
  const isAdmin = user?.is_admin || false;

  return (
    <Tab.Navigator
      screenOptions={{
        tabBarActiveTintColor: '#3498DB',
        tabBarInactiveTintColor: '#7F8C8D',
        tabBarStyle: {
          backgroundColor: '#FFFFFF',
          borderTopWidth: 1,
          borderTopColor: '#E1E8ED',
          paddingBottom: 5,
          height: 60,
        },
      }}
    >
      <Tab.Screen 
        name="AI Assistant" 
        component={AIDashboardScreen} 
        options={{ 
          headerShown: false,
          tabBarIcon: ({ focused }) => (
            <Text style={{ fontSize: 20 }}>🤖</Text>
          ),
        }} 
      />
      <Tab.Screen 
        name="Practice" 
        component={PracticeStackNavigator} 
        options={{ 
          headerShown: false,
          tabBarIcon: ({ focused }) => (
            <Text style={{ fontSize: 20 }}>📝</Text>
          ),
        }} 
      />
      <Tab.Screen 
        name="Learn" 
        component={LearnStackNavigator} 
        options={{ 
          headerShown: false,
          tabBarIcon: ({ focused }) => (
            <Text style={{ fontSize: 20 }}>📚</Text>
          ),
        }} 
      />
      <Tab.Screen 
        name="Search" 
        component={SearchScreen} 
        options={{
          tabBarIcon: ({ focused }) => (
            <Text style={{ fontSize: 20 }}>🔍</Text>
          ),
        }} 
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen} 
        options={{
          tabBarIcon: ({ focused }) => (
            <Text style={{ fontSize: 20 }}>👤</Text>
          ),
        }} 
      />
      {isAdmin && (
        <Tab.Screen 
          name="Admin" 
          component={AdminStackNavigator} 
          options={{ 
            headerShown: false,
            tabBarIcon: ({ focused }) => (
              <Text style={{ fontSize: 20 }}>⚙️</Text>
            ),
          }} 
        />
      )}
    </Tab.Navigator>
  );
};

export default MainTabNavigator;
