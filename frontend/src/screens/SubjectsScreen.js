import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet } from 'react-native';
import apiClient from '../api/client';

const SubjectsScreen = ({ navigation }) => {
  const [subjects, setSubjects] = useState([]);

  useEffect(() => {
    const fetchSubjects = async () => {
      try {
        // const response = await apiClient.get('/subjects');
        // setSubjects(response.data);
        setSubjects([
          { id: 1, name: 'Mathematics' },
          { id: 2, name: 'Physics' },
        ]);
      } catch (error) {
        console.error(error);
      }
    };
    fetchSubjects();
  }, []);

  const renderItem = ({ item }) => (
    <TouchableOpacity
      style={styles.item}
      onPress={() => navigation.navigate('Topics', { subjectId: item.id })}
    >
      <Text style={styles.title}>{item.name}</Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={subjects}
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

export default SubjectsScreen;
