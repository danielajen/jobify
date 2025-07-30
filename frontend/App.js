import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  StatusBar,
  SafeAreaView,
  Dimensions
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { API_URL } from './config';
import { UserProvider } from './context/UserContext';
import JobSwiper from './components/JobSwiper';
import FavoriteCompanies from './components/FavoriteCompanies';
import RecruiterNetwork from './components/RecruiterNetwork';
import ProfileScreen from './components/ProfileScreen';
import SavedJobs from './components/SavedJobs';
import ResourcesScreen from './components/ResourcesScreen';

const { width, height } = Dimensions.get('window');

export default function App() {
  const [activeTab, setActiveTab] = useState('jobs');
  const [savedJobs, setSavedJobs] = useState([]);
  const [linkedInConnected, setLinkedInConnected] = useState(false);

  // Check LinkedIn connection status on app start and periodically
  useEffect(() => {
    checkLinkedInStatus();
    
    // Check status every 3 seconds
    const interval = setInterval(() => {
      checkLinkedInStatus();
    }, 3000);
    
    return () => clearInterval(interval);
  }, []);

  const checkLinkedInStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/auth/status`);
      const data = await response.json();
      setLinkedInConnected(data.linkedin_connected || false);
    } catch (error) {
      console.log('LinkedIn status check failed:', error);
    }
  };

  const handleSaveJob = (job) => {
    setSavedJobs(prev => {
      const exists = prev.find(savedJob => savedJob.id === job.id);
      if (exists) {
        return prev.filter(savedJob => savedJob.id !== job.id);
      } else {
        return [...prev, job];
      }
    });
  };

  const handleRemoveJob = (jobId) => {
    setSavedJobs(prev => prev.filter(job => job.id !== jobId));
  };

  const handleApplyJob = (job) => {
    Alert.alert('Job Applied', `Applied to ${job.title} at ${job.company}`);
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'jobs':
        return <JobSwiper onSaveJob={handleSaveJob} onApplyJob={handleApplyJob} />;
      case 'favorites':
        return <FavoriteCompanies onApply={handleApplyJob} />;
      case 'network':
        return <RecruiterNetwork linkedInConnected={linkedInConnected} onLinkedInConnect={checkLinkedInStatus} />;
      case 'saved':
        return <SavedJobs jobs={savedJobs} onRemoveJob={handleRemoveJob} onApplyJob={handleApplyJob} />;
      case 'profile':
        return <ProfileScreen />;
      case 'resources':
        return <ResourcesScreen />;
      default:
        return <JobSwiper onSaveJob={handleSaveJob} onApplyJob={handleApplyJob} />;
    }
  };

  const getTabIcon = (tabName) => {
    const isActive = activeTab === tabName;
    const iconColor = isActive ? '#667eea' : '#999';

    switch (tabName) {
      case 'jobs':
        return <Ionicons name="briefcase" size={24} color={iconColor} />;
      case 'favorites':
        return <Ionicons name="heart" size={24} color={iconColor} />;
      case 'network':
        return <Ionicons name="people" size={24} color={iconColor} />;
      case 'saved':
        return <Ionicons name="bookmark" size={24} color={iconColor} />;
      case 'profile':
        return <Ionicons name="person" size={24} color={iconColor} />;
      case 'resources':
        return <Ionicons name="library" size={24} color={iconColor} />;
      default:
        return <Ionicons name="briefcase" size={24} color={iconColor} />;
    }
  };

  return (
    <UserProvider>
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="light-content" backgroundColor="#667eea" />

        {/* Top Navigation Bar */}
        <View style={styles.topNav}>
          <View style={styles.topNavContent}>
            <Text style={styles.appTitle}>JobSwipe</Text>
            <View style={styles.topNavTabs}>
              <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                {['jobs', 'favorites', 'network', 'saved', 'profile', 'resources'].map((tab) => (
                  <TouchableOpacity
                    key={tab}
                    style={[styles.topNavTab, activeTab === tab && styles.activeTopNavTab]}
                    onPress={() => setActiveTab(tab)}
                  >
                    <View style={styles.tabIconContainer}>
                      {getTabIcon(tab)}
                    </View>
                    <Text style={[styles.topNavTabText, activeTab === tab && styles.activeTopNavTabText]}>
                      {tab.charAt(0).toUpperCase() + tab.slice(1)}
                    </Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>
            </View>
          </View>
        </View>

        {/* Main Content */}
        <View style={styles.content}>
          {renderTabContent()}
        </View>
      </SafeAreaView>
    </UserProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  topNav: {
    backgroundColor: '#667eea',
    paddingTop: 10,
    paddingBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 5,
  },
  topNavContent: {
    paddingHorizontal: 20,
  },
  appTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
    textAlign: 'center',
    marginBottom: 15,
    letterSpacing: 1,
  },
  topNavTabs: {
    flexDirection: 'row',
  },
  topNavTab: {
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginRight: 15,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    minWidth: 60,
  },
  activeTopNavTab: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.3)',
  },
  tabIconContainer: {
    marginBottom: 4,
  },
  topNavTabText: {
    fontSize: 11,
    color: 'rgba(255, 255, 255, 0.8)',
    fontWeight: '600',
    textAlign: 'center',
  },
  activeTopNavTabText: {
    color: 'white',
    fontWeight: 'bold',
  },
  content: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
});