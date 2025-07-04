import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import apiClient from '../api/client';

const QuestionDetailScreen = ({ route }) => {
  const { questionId } = route.params;
  const [question, setQuestion] = useState(null);

  useEffect(() => {
    const fetchQuestion = async () => {
      try {
        // const response = await apiClient.get(`/questions/${questionId}`);
        // setQuestion(response.data);
        setQuestion({
          id: 1,
          title: 'What is the derivative of x^2?',
          content: 'This is the content of the question.',
          answer: '2x',
        });
      } catch (error) {
        console.error(error);
      }
    };
    fetchQuestion();
  }, [questionId]);

  if (!question) {
    return (
      <View style={styles.container}>
        <Text>Loading...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{question.title}</Text>
      <Text style={styles.content}>{question.content}</Text>
      <Text style={styles.answer}>Answer: {question.answer}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  content: {
    fontSize: 18,
    marginBottom: 16,
  },
  answer: {
    fontSize: 18,
    fontWeight: 'bold',
  },
});

export default QuestionDetailScreen;
