import React, { useState } from 'react';
import { View, Text, TextInput, FlatList, StyleSheet, TouchableOpacity } from 'react-native';

const SearchScreen = () => {
  const [searchText, setSearchText] = useState('');
  const [searchResults, setSearchResults] = useState([]);

  const handleSearch = (text) => {
    setSearchText(text);
    // Simulate API call for search results
    if (text.length > 2) {
      setSearchResults([
        { id: 1, title: `Question about ${text}` },
        { id: 2, title: `Subject related to ${text}` },
      ]);
    } else {
      setSearchResults([]);
    }
  };

  const renderItem = ({ item }) => (
    <TouchableOpacity style={styles.resultItem}>
      <Text style={styles.resultTitle}>{item.title}</Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <TextInput
        style={styles.searchInput}
        placeholder="Search questions, subjects, topics..."
        value={searchText}
        onChangeText={handleSearch}
      />
      <FlatList
        data={searchResults}
        renderItem={renderItem}
        keyExtractor={(item) => item.id.toString()}
        ListEmptyComponent={
          <Text style={styles.noResultsText}>Type to search...</Text>
        }
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#f5f5f5',
  },
  searchInput: {
    height: 40,
    borderColor: 'gray',
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 10,
    marginBottom: 16,
  },
  resultItem: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 1.41,
    elevation: 2,
  },
  resultTitle: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  noResultsText: {
    textAlign: 'center',
    marginTop: 20,
    fontSize: 16,
    color: '#888',
  },
});

export default SearchScreen;