import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet, TouchableOpacity } from 'react-native';
import apiClient from '../api/client';

const TopicsScreen = ({ route, navigation }) => {
  const { subjectId } = route.params;
  const [topics, setTopics] = useState([]);

  useEffect(() => {
    const fetchTopics = async () => {
      try {
        // const response = await apiClient.get(`/subjects/${subjectId}/topics`);
        // setTopics(response.data);
        setTopics([
          { id: 1, name: 'Algebra' },
          { id: 2, name: 'Calculus' },
        ]);
      } catch (error) {
        console.error(error);
      }
    };
    fetchTopics();
  }, [subjectId]);

  const renderItem = ({ item }) => (
    <TouchableOpacity
      style={styles.item}
      onPress={() => navigation.navigate('QuestionList', { topicId: item.id })}
    >
      <Text style={styles.title}>{item.name}</Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={topics}
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

export default TopicsScreen;
