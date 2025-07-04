import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const PracticeScreen = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Practice</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
  },
});

export default PracticeScreen;
