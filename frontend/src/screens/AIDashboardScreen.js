import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useSelector } from 'react-redux';
import { aiService } from '../api/aiService';

const AIDashboardScreen = ({ navigation }) => {
  const [message, setMessage] = useState('');
  const [conversation, setConversation] = useState([
    {
      id: 1,
      type: 'ai',
      text: "Hello! I'm your AI study assistant. Ask me anything about your subjects, practice questions, or need help with specific topics. How can I help you today?",
      timestamp: new Date(),
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const scrollViewRef = useRef();
  const user = useSelector((state) => state.auth.user);

  // Sample quick actions
  const quickActions = [
    { id: 1, title: 'Start Practice', icon: '📝', action: () => navigation.navigate('Practice') },
    { id: 2, title: 'Browse Subjects', icon: '📚', action: () => navigation.navigate('Learn', { screen: 'Subjects' }) },
    { id: 3, title: 'Search Questions', icon: '🔍', action: () => navigation.navigate('Search') },
    { id: 4, title: 'Upload Questions', icon: '📤', action: () => navigation.navigate('Learn', { screen: 'Upload' }) },
    { id: 5, title: 'Course Materials', icon: '📖', action: () => navigation.navigate('Learn', { screen: 'CourseMaterials' }) },
  ];

  const handleSendMessage = async () => {
    if (!message.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      text: message.trim(),
      timestamp: new Date(),
    };

    setConversation(prev => [...prev, userMessage]);
    setMessage('');
    setIsLoading(true);

    try {
      // Call AI service - you'll need to implement this
      const aiResponse = await aiService.askQuestion({
        question: userMessage.text,
        context: 'general_study_help',
      });

      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        text: aiResponse.answer || "I understand your question. Let me help you with that! For now, I'm still learning but I'll be able to provide detailed answers about your subjects and practice questions soon.",
        timestamp: new Date(),
      };

      setConversation(prev => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'ai',
        text: "I'm sorry, I'm having trouble connecting right now. Please try again in a moment. In the meantime, you can use the quick actions below to navigate the app!",
        timestamp: new Date(),
      };
      setConversation(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderMessage = (msg) => (
    <View key={msg.id} style={[styles.messageContainer, msg.type === 'user' ? styles.userMessage : styles.aiMessage]}>
      <Text style={[styles.messageText, msg.type === 'user' ? styles.userMessageText : styles.aiMessageText]}>
        {msg.text}
      </Text>
      <Text style={styles.timestamp}>
        {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
      </Text>
    </View>
  );

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    setTimeout(() => {
      scrollViewRef.current?.scrollToEnd({ animated: true });
    }, 100);
  }, [conversation]);

  return (
    <KeyboardAvoidingView style={styles.container} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>My-Ace</Text>
        <Text style={styles.headerSubtitle}>
          Welcome back, {user?.username || 'OpenCode'}! 😎
        </Text>
      </View>

      {/* Quick Actions */}
      <View style={styles.quickActionsContainer}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.quickActionsScroll}>
          {quickActions.map((action) => (
            <TouchableOpacity key={action.id} style={styles.quickActionCard} onPress={action.action}>
              <Text style={styles.quickActionIcon}>{action.icon}</Text>
              <Text style={styles.quickActionTitle}>{action.title}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Chat Interface */}
      <View style={styles.chatContainer}>
        <Text style={styles.sectionTitle}>Ask AI Anything</Text>
        
        <ScrollView
          ref={scrollViewRef}
          style={styles.conversationContainer}
          showsVerticalScrollIndicator={false}
        >
          {conversation.map(renderMessage)}
          {isLoading && (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="small" color="#3498DB" />
              <Text style={styles.loadingText}>AI is thinking...</Text>
            </View>
          )}
        </ScrollView>

        {/* Message Input */}
        <View style={styles.inputContainer}>
          <TextInput
            style={styles.textInput}
            value={message}
            onChangeText={setMessage}
            placeholder="Ask about subjects, practice questions, or study tips..."
            multiline
            maxLength={500}
            editable={!isLoading}
          />
          <TouchableOpacity
            style={[styles.sendButton, (!message.trim() || isLoading) && styles.sendButtonDisabled]}
            onPress={handleSendMessage}
            disabled={!message.trim() || isLoading}
          >
            <Text style={styles.sendButtonText}>Send</Text>
          </TouchableOpacity>
        </View>
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  header: {
    backgroundColor: '#3498DB',
    paddingTop: 50,
    paddingBottom: 20,
    paddingHorizontal: 20,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#FFFFFF',
    opacity: 0.9,
  },
  quickActionsContainer: {
    paddingVertical: 15,
    paddingLeft: 20,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E1E8ED',
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2C3E50',
    marginBottom: 10,
  },
  quickActionsScroll: {
    paddingRight: 20,
  },
  quickActionCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 15,
    marginRight: 12,
    alignItems: 'center',
    minWidth: 100,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    borderWidth: 1,
    borderColor: '#E1E8ED',
  },
  quickActionIcon: {
    fontSize: 24,
    marginBottom: 8,
  },
  quickActionTitle: {
    fontSize: 12,
    fontWeight: '500',
    color: '#2C3E50',
    textAlign: 'center',
  },
  chatContainer: {
    flex: 1,
    padding: 20,
  },
  conversationContainer: {
    flex: 1,
    marginBottom: 15,
  },
  messageContainer: {
    marginBottom: 15,
    maxWidth: '80%',
    padding: 12,
    borderRadius: 12,
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: '#3498DB',
  },
  aiMessage: {
    alignSelf: 'flex-start',
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E1E8ED',
  },
  messageText: {
    fontSize: 16,
    lineHeight: 22,
    marginBottom: 4,
  },
  userMessageText: {
    color: '#FFFFFF',
  },
  aiMessageText: {
    color: '#2C3E50',
  },
  timestamp: {
    fontSize: 11,
    opacity: 0.7,
    alignSelf: 'flex-end',
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    marginBottom: 15,
  },
  loadingText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#7F8C8D',
    fontStyle: 'italic',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E1E8ED',
    padding: 8,
  },
  textInput: {
    flex: 1,
    fontSize: 16,
    paddingHorizontal: 12,
    paddingVertical: 8,
    maxHeight: 100,
    color: '#2C3E50',
  },
  sendButton: {
    backgroundColor: '#3498DB',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 8,
    marginLeft: 8,
  },
  sendButtonDisabled: {
    backgroundColor: '#BDC3C7',
  },
  sendButtonText: {
    color: '#FFFFFF',
    fontWeight: '600',
    fontSize: 14,
  },
});

export default AIDashboardScreen; 