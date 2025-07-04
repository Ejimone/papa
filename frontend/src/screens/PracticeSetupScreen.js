import React, { useState } from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';

const PracticeSetupScreen = ({ navigation }) => {
  const [subject, setSubject] = useState(null);
  const [difficulty, setDifficulty] = useState(null);
  const [numQuestions, setNumQuestions] = useState(10);

  const startPractice = () => {
    navigation.navigate('PracticeSession', {
      subject,
      difficulty,
      numQuestions,
    });
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Practice Setup</Text>
      {/* TODO: Add subject, difficulty, and number of questions selection */}
      <Button title="Start Practice" onPress={startPractice} />
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
});

export default PracticeSetupScreen;
