import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';

import PracticeSetupScreen from '../screens/PracticeSetupScreen';
import PracticeSessionScreen from '../screens/PracticeSessionScreen';
import SessionSummaryScreen from '../screens/SessionSummaryScreen';

const Stack = createStackNavigator();

const PracticeStackNavigator = () => {
  return (
    <Stack.Navigator>
      <Stack.Screen name="PracticeSetup" component={PracticeSetupScreen} options={{ title: 'Practice Setup' }} />
      <Stack.Screen name="PracticeSession" component={PracticeSessionScreen} options={{ title: 'Practice Session' }} />
      <Stack.Screen name="SessionSummary" component={SessionSummaryScreen} options={{ title: 'Session Summary' }} />
    </Stack.Navigator>
  );
};

export default PracticeStackNavigator;
