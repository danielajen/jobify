import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  FlatList, 
  Button, 
  Linking, 
  ActivityIndicator,
  RefreshControl
} from 'react-native';
import { API_URL } from '../config';

const ResourcesScreen = () => {
  const [resources, setResources] = useState({
    github_repos: [],
    job_portals: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchResources = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${API_URL}/resources`);
      
      if (!response.ok) {
        throw new Error(`Server returned ${response.status} status`);
      }
      
      const data = await response.json();
      setResources(data);
    } catch (err) {
      console.error('Fetch error:', err);
      setError(`Failed to load resources: ${err.message || 'Unknown error'}`);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchResources();
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchResources();
  };

  const renderRepoItem = ({ item }) => (
    <View style={styles.item}>
      <Text style={styles.itemTitle}>{item.name}</Text>
      <Text style={styles.itemDescription}>
        {item.description ? item.description.substring(0, 100) + '...' : 'No description'}
      </Text>
      <Button 
        title="View Repository" 
        onPress={() => Linking.openURL(item.url)} 
        color="#0366d6"
      />
    </View>
  );

  const renderPortalItem = ({ item }) => (
    <View style={styles.item}>
      <Text style={styles.itemTitle}>{item.name}</Text>
      <Button 
        title="Visit Portal" 
        onPress={() => Linking.openURL(item.url)} 
        color="#28a745"
      />
    </View>
  );

  if (loading && !refreshing) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#0000ff" />
        <Text style={styles.loadingText}>Loading resources...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.centerContainer}>
        <Text style={styles.errorText}>❌ {error}</Text>
        <Text style={styles.helpText}>
          Make sure your backend is running at {API_URL}
        </Text>
        <Button 
          title="Retry" 
          onPress={fetchResources} 
          style={styles.retryButton}
        />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Job Search Resources</Text>
      
      <Text style={styles.sectionTitle}>GitHub Repositories</Text>
      <FlatList
        data={resources.github_repos}
        keyExtractor={(item, index) => index.toString()}
        renderItem={renderRepoItem}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            colors={['#0000ff']}
          />
        }
      />
      
      <Text style={styles.sectionTitle}>Job Portals</Text>
      <FlatList
        data={resources.job_portals}
        keyExtractor={(item, index) => index.toString()}
        renderItem={renderPortalItem}
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
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#333',
    textAlign: 'center',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginTop: 15,
    marginBottom: 10,
    color: '#444',
    paddingBottom: 5,
    borderBottomWidth: 1,
    borderBottomColor: '#ddd',
  },
  item: {
    backgroundColor: 'white',
    padding: 15,
    marginBottom: 10,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  itemTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 5,
    color: '#222',
  },
  itemDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 10,
  },
  errorText: {
    color: '#d9534f',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    textAlign: 'center',
  },
  helpText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 20,
    textAlign: 'center',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#555',
  },
  retryButton: {
    marginTop: 10,
    width: 120,
  },
});

export default ResourcesScreen;