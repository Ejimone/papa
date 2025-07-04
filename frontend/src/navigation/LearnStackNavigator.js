import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';

import SubjectsScreen from '../screens/SubjectsScreen';
import TopicsScreen from '../screens/TopicsScreen';

import QuestionListScreen from '../screens/QuestionListScreen';
import QuestionDetailScreen from '../screens/QuestionDetailScreen';

const Stack = createStackNavigator();

const LearnStackNavigator = () => {
  return (
    <Stack.Navigator>
      <Stack.Screen name="Subjects" component={SubjectsScreen} />
      <Stack.Screen name="Topics" component={TopicsScreen} />
      <Stack.Screen name="QuestionList" component={QuestionListScreen} />
      <Stack.Screen name="QuestionDetail" component={QuestionDetailScreen} />
    </Stack.Navigator>
  );
};

export default LearnStackNavigator;
