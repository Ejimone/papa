import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet } from 'react-native';
import apiClient from '../api/client';

const QuestionListScreen = ({ route, navigation }) => {
  const { topicId } = route.params;
  const [questions, setQuestions] = useState([]);

  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        // const response = await apiClient.get(`/topics/${topicId}/questions`);
        // setQuestions(response.data);
        setQuestions([
          { id: 1, title: 'What is the derivative of x^2?' },
          { id: 2, title: 'What is the integral of x^2?' },
        ]);
      } catch (error) {
        console.error(error);
      }
    };
    fetchQuestions();
  }, [topicId]);

  const renderItem = ({ item }) => (
    <TouchableOpacity
      style={styles.item}
      onPress={() => navigation.navigate('QuestionDetail', { questionId: item.id })}
    >
      <Text style={styles.title}>{item.title}</Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={questions}
        renderItem={renderItem}
        keyExtractor={(item) => item.id.toString()}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  item: {
    backgroundColor: '#f9c2ff',
    padding: 20,
    marginVertical: 8,
    marginHorizontal: 16,
  },
  title: {
    fontSize: 24,
  },
});

export default QuestionListScreen;
