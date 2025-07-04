import React from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';

const SessionSummaryScreen = ({ route, navigation }) => {
  const { score, totalQuestions } = route.params;
  const percentage = (score / totalQuestions) * 100;

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Session Summary</Text>
      <Text style={styles.summaryText}>You scored {score} out of {totalQuestions} questions.</Text>
      <Text style={styles.summaryText}>Accuracy: {percentage.toFixed(2)}%</Text>
      <Button title="Go to Dashboard" onPress={() => navigation.navigate('Dashboard')} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  title: {
    fontSize: 24,
    marginBottom: 16,
  },
  summaryText: {
    fontSize: 18,
    marginBottom: 8,
  },
});

export default SessionSummaryScreen;
