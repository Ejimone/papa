import React, { useEffect } from 'react';
import { Provider, useDispatch } from 'react-redux';
import { View, ActivityIndicator, StyleSheet, Text } from 'react-native';
import { store } from './src/store';
import { checkAuthStatus } from './src/store/authSlice';
import AppNavigator from './src/navigation/AppNavigator';

// Loading component
const LoadingScreen = () => (
  <View style={styles.loadingContainer}>
    <ActivityIndicator size="large" color="#3498DB" />
    <Text style={styles.loadingText}>Loading...</Text>
  </View>
);

// App initialization component
const AppInitializer = () => {
  const dispatch = useDispatch();
  
  useEffect(() => {
    // Check authentication status on app start
    dispatch(checkAuthStatus());
  }, [dispatch]);

  return <AppNavigator />;
};

export default function App() {
  return (
    <Provider store={store}>
      <AppInitializer />
    </Provider>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F8F9FA',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#7F8C8D',
  },
});
