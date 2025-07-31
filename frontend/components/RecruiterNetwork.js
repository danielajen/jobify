import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  ScrollView,
  TextInput,
  FlatList,
  Dimensions,
  Linking
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { API_URL } from '../config';

const { width, height } = Dimensions.get('window');

const RecruiterNetwork = ({ linkedInConnected, onLinkedInConnect }) => {
  const [connections, setConnections] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [outreachHistory, setOutreachHistory] = useState([]);
  const [activeTab, setActiveTab] = useState('connections');
  const [emailContent, setEmailContent] = useState('');
  const [selectedConnection, setSelectedConnection] = useState(null);
  const [generatingEmail, setGeneratingEmail] = useState(false);
  const [sendingEmail, setSendingEmail] = useState(false);
  const [scrapingStatus, setScrapingStatus] = useState('');

  // Advanced search filters
  const [selectedLocation, setSelectedLocation] = useState('');
  const [selectedCompany, setSelectedCompany] = useState('');
  const [selectedJobTitle, setSelectedJobTitle] = useState('');
  const [selectedUniversity, setSelectedUniversity] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [alumniOnly, setAlumniOnly] = useState(false);

  // Filter options
  const locationOptions = [
    'Toronto, Ontario, Canada',
    'Oakville, Ontario, Canada',
    'Mississauga, Ontario, Canada',
    'Brampton, Ontario, Canada',
    'Vaughan, Ontario, Canada',
    'Markham, Ontario, Canada',
    'Richmond Hill, Ontario, Canada',
    'Burlington, Ontario, Canada',
    'Hamilton, Ontario, Canada',
    'Kitchener, Ontario, Canada',
    'Waterloo, Ontario, Canada',
    'London, Ontario, Canada',
    'Ottawa, Ontario, Canada',
    'Montreal, Quebec, Canada',
    'Vancouver, British Columbia, Canada',
    'Calgary, Alberta, Canada',
    'Edmonton, Alberta, Canada'
  ];

  const companyOptions = [
    'Google', 'Apple', 'Microsoft', 'Amazon', 'Meta', 'Netflix', 'Twitter',
    'Uber', 'Airbnb', 'Stripe', 'Square', 'Palantir', 'Databricks',
    'Snowflake', 'MongoDB', 'Atlassian', 'Slack', 'Zoom', 'Salesforce',
    'Adobe', 'Intel', 'NVIDIA', 'AMD', 'Oracle', 'IBM', 'Cisco',
    'Shopify', 'RBC', 'TD Bank', 'Scotiabank', 'BMO', 'CIBC',
    'Bell', 'Rogers', 'Telus', 'Cogeco', 'Shaw', 'Videotron',
    'Canadian Tire', 'Loblaw', 'Sobeys', 'Metro', 'Walmart Canada',
    'Costco Canada', 'Home Depot Canada', 'Air Canada', 'WestJet',
    'Manulife', 'Sun Life', 'Great-West Life', 'Canada Life',
    'Desjardins', 'Co-operators', 'Intact Financial', 'Aviva Canada'
  ];

  const jobTitleOptions = [
    'Software Engineer', 'Software Developer', 'Full Stack Developer',
    'Frontend Developer', 'Backend Developer', 'DevOps Engineer',
    'Data Scientist', 'Data Engineer', 'Machine Learning Engineer',
    'Product Manager', 'Product Owner', 'Technical Product Manager',
    'Engineering Manager', 'Tech Lead', 'Senior Software Engineer',
    'Principal Engineer', 'Staff Engineer', 'Senior Developer',
    'Lead Developer', 'Architect', 'Solutions Architect',
    'QA Engineer', 'Test Engineer', 'Quality Assurance Engineer',
    'UI/UX Designer', 'UX Designer', 'UI Designer', 'Product Designer',
    'Technical Writer', 'Developer Advocate', 'Site Reliability Engineer',
    'Cloud Engineer', 'Infrastructure Engineer', 'Security Engineer',
    'Mobile Developer', 'iOS Developer', 'Android Developer',
    'React Developer', 'Python Developer', 'Java Developer',
    'Node.js Developer', 'Ruby Developer', 'PHP Developer',
    'C++ Developer', 'C# Developer', '.NET Developer'
  ];

  const universityOptions = [
    'University of Toronto', 'University of Waterloo', 'University of British Columbia',
    'McGill University', 'University of Alberta', 'University of Ottawa',
    'Western University', 'McMaster University', 'Queen\'s University',
    'University of Calgary', 'University of Victoria', 'Simon Fraser University',
    'Carleton University', 'York University', 'Ryerson University',
    'University of Guelph', 'University of Western Ontario', 'Western Ontario',
    'University of Windsor', 'Brock University', 'Trent University',
    'Wilfrid Laurier University', 'University of Ontario Institute of Technology',
    'OCAD University', 'Ontario College of Art and Design',
    'Sheridan College', 'Seneca College', 'Humber College',
    'George Brown College', 'Centennial College', 'Algonquin College'
  ];

  useEffect(() => {
    if (linkedInConnected) {
      fetchOutreachHistory();
    }
  }, [linkedInConnected]);

  // Add periodic status checking
  useEffect(() => {
    const checkStatusInterval = setInterval(() => {
      checkLinkedInStatus();
    }, 5000); // Check every 5 seconds

    return () => clearInterval(checkStatusInterval);
  }, []);

  const checkLinkedInStatus = async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const response = await fetch(`${API_URL}/auth/status`, {
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`Server returned ${response.status} status`);
      }

      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        throw new Error('Server returned non-JSON response');
      }

      const data = await response.json();
      if (data.linkedin_connected) {
        onLinkedInConnect();
        // Refresh outreach history if we just got connected
        if (!linkedInConnected) {
          fetchOutreachHistory();
        }
      }
    } catch (error) {
      console.log('LinkedIn status check failed:', error);
      // Don't block the app if LinkedIn check fails
    }
  };

  const connectLinkedIn = async () => {
    try {
      setLoading(true);

      // Get LinkedIn OpenID Connect URL from backend
      const response = await fetch(`${API_URL}/linkedin/auth?user_id=user`);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `LinkedIn OpenID Connect failed: ${response.status}`);
      }

      const data = await response.json();

      if (data.auth_url) {
        // Open LinkedIn OpenID Connect in browser
        Alert.alert(
          'Sign In with LinkedIn',
          'You will be redirected to LinkedIn to sign in using OpenID Connect. After signing in, you will be redirected back to the app.',
          [
            { text: 'Cancel', style: 'cancel' },
            {
              text: 'Sign In',
              onPress: async () => {
                try {
                  // Open LinkedIn OpenID Connect URL in browser
                  await Linking.openURL(data.auth_url);

                  // Show instructions
                  Alert.alert(
                    'Complete LinkedIn Sign In',
                    'Please complete the LinkedIn sign in using OpenID Connect in your browser. You will be automatically redirected back to the app.',
                    [{ text: 'OK' }]
                  );

                  // Check status after a delay
                  setTimeout(() => {
                    checkLinkedInStatus();
                  }, 3000);

                } catch (error) {
                  console.error('Failed to open LinkedIn URL:', error);
                  Alert.alert('Error', 'Failed to open LinkedIn sign in page. Please try again.');
                }
              }
            }
          ]
        );
      } else {
        throw new Error('No authorization URL received from server');
      }
    } catch (error) {
      console.error('LinkedIn OpenID Connect error:', error);
      Alert.alert('Sign In Failed', `Failed to connect LinkedIn: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchOutreachHistory = async () => {
    try {
      const response = await fetch(`${API_URL}/outreach-history?user_id=user`);

      if (response.ok) {
        const data = await response.json();
        setOutreachHistory(data || []);
      }
    } catch (error) {
      console.error('Fetch outreach history error:', error);
    }
  };

  const generateEmailTemplate = async (connection) => {
    try {
      setSelectedConnection(connection);
      setGeneratingEmail(true);

      const response = await fetch(`${API_URL}/generate-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          connection_name: connection.name,
          connection_title: connection.title,
          connection_company: connection.company,
          user_name: 'Daniel Ajenifuja'
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to generate email');
      }

      const data = await response.json();
      setEmailContent(data.email_content || '');
      Alert.alert('Success', 'AI-generated email template created!');
    } catch (error) {
      console.error('Email generation error:', error);
      Alert.alert('Error', error.message);
    } finally {
      setGeneratingEmail(false);
    }
  };

  const sendOutreach = async () => {
    if (!selectedConnection || !emailContent.trim()) {
      Alert.alert('Error', 'Please select a connection and generate an email first.');
      return;
    }

    try {
      setSendingEmail(true);

      const response = await fetch(`${API_URL}/send-outreach`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          recipient_email: selectedConnection.email || 'recipient@example.com',
          recipient_name: selectedConnection.name,
          email_content: emailContent,
          user_id: 'user',
          connection_id: selectedConnection.id,
          job_title: 'Software Engineer',
          company_name: selectedConnection.company
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to send outreach');
      }

      const data = await response.json();
      Alert.alert('Success', `Email sent successfully via SendGrid! Email ID: ${data.email_id || 'unknown'}`);

      // Refresh outreach history
      fetchOutreachHistory();

      // Clear form
      setEmailContent('');
      setSelectedConnection(null);
    } catch (error) {
      console.error('Send outreach error:', error);
      Alert.alert('Error', error.message);
    } finally {
      setSendingEmail(false);
    }
  };

  const searchProfiles = async () => {
    try {
      setSearchLoading(true);
      setSearchResults([]);
      setScrapingStatus('Searching LinkedIn profiles...');

      // Build filters based on selected options
      const filters = {};

      if (selectedLocation) {
        filters.location = [selectedLocation];
      }

      if (selectedCompany) {
        filters.company = [selectedCompany];
      }

      if (selectedJobTitle) {
        filters.job_title = [selectedJobTitle];
      }

      if (alumniOnly) {
        filters.alumni = true;
      }

      // Use the scraping endpoint for real LinkedIn data
      const response = await fetch(`${API_URL}/linkedin/scrape-profiles`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: searchQuery || 'tech professionals',
          user_id: 'user',
          filters: filters,
          max_results: 50
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Search failed');
      }

      const data = await response.json();
      setSearchResults(data.profiles || []);
      setScrapingStatus('');

      if (data.profiles?.length === 0) {
        Alert.alert('No Results', 'No profiles found matching your search criteria. Try adjusting your filters.');
      } else {
        Alert.alert('Success', `Found ${data.profiles.length} profiles! Scraped at ${new Date().toLocaleTimeString()}`);
      }
    } catch (error) {
      console.error('Search error:', error);
      setScrapingStatus('Scraping failed. Try different filters.');
      Alert.alert('Error', error.message);
    } finally {
      setSearchLoading(false);
    }
  };

  const scrapeBigTechProfiles = async () => {
    try {
      setLoading(true);
      setScrapingStatus('Scraping Google employees in Toronto...');
      setConnections([]);

      const response = await fetch(`${API_URL}/linkedin/scrape-company`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company_name: 'Google',
          location: 'Toronto, Ontario, Canada',
          max_results: 50,
          user_id: 'user'
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to scrape profiles');
      }

      const data = await response.json();
      setConnections(data.profiles || []);
      setScrapingStatus(`Found ${data.profiles.length} profiles!`);

      Alert.alert('Success', `Scraped ${data.profiles.length} Google employees in Toronto!`);
    } catch (error) {
      console.error('Scraping error:', error);
      setScrapingStatus('Scraping failed. Using real-time search instead.');
      Alert.alert('Error', error.message);
    } finally {
      setLoading(false);
    }
  };

  const scrapeTorontoProfessionals = async () => {
    try {
      setLoading(true);
      setScrapingStatus('Scraping Toronto professionals...');
      setConnections([]);

      const response = await fetch(`${API_URL}/linkedin/scrape-location`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          location: 'Toronto, Ontario, Canada',
          job_titles: ['Software Engineer', 'Product Manager', 'Data Scientist'],
          max_results: 100,
          user_id: 'user'
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to scrape profiles');
      }

      const data = await response.json();
      setConnections(data.profiles || []);
      setScrapingStatus(`Found ${data.profiles.length} profiles!`);

      Alert.alert('Success', `Scraped ${data.profiles.length} Toronto professionals!`);
    } catch (error) {
      console.error('Scraping error:', error);
      setScrapingStatus('Scraping failed. Using real-time search instead.');
      Alert.alert('Error', error.message);
    } finally {
      setLoading(false);
    }
  };

  const renderConnectionCard = ({ item }) => (
    <View style={styles.connectionCard}>
      <View style={styles.connectionHeader}>
        <View style={styles.connectionAvatar}>
          <Text style={styles.avatarText}>
            {item.name.split(' ').map(n => n[0]).join('')}
          </Text>
        </View>
        <View style={styles.connectionInfo}>
          <Text style={styles.connectionName}>{item.name}</Text>
          <Text style={styles.connectionTitle}>{item.title}</Text>
          <Text style={styles.connectionCompany}>{item.company}</Text>
        </View>
        {item.is_alumni && (
          <View style={styles.alumniBadge}>
            <Ionicons name="school" size={16} color="#667eea" />
            <Text style={styles.alumniText}>Alumni</Text>
          </View>
        )}
      </View>

      <View style={styles.connectionMeta}>
        <View style={styles.metaItem}>
          <Ionicons name="location-outline" size={16} color="#666" />
          <Text style={styles.metaText}>{item.location}</Text>
        </View>
        <View style={styles.metaItem}>
          <Ionicons name="people-outline" size={16} color="#666" />
          <Text style={styles.metaText}>
            {item.mutual_connections > 0
              ? `${item.mutual_connections} mutual connections`
              : 'No mutual connections'
            }
          </Text>
        </View>
      </View>

      <View style={styles.connectionActions}>
        <TouchableOpacity
          style={[styles.actionButton, styles.messageButton]}
          onPress={() => generateEmailTemplate(item)}
          disabled={generatingEmail}
        >
          {generatingEmail ? (
            <ActivityIndicator size="small" color="#667eea" />
          ) : (
            <>
              <Ionicons name="mail-outline" size={20} color="#667eea" />
              <Text style={styles.actionButtonText}>Generate Email</Text>
            </>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.actionButton, styles.viewButton]}
          onPress={() => {
            if (item.profile_url) {
              Linking.openURL(item.profile_url);
            } else {
              Alert.alert('View Profile', `View ${item.name}'s profile`);
            }
          }}
        >
          <Ionicons name="eye-outline" size={20} color="#51cf66" />
          <Text style={styles.actionButtonText}>View</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  const renderOutreachHistoryItem = ({ item }) => (
    <View style={styles.historyCard}>
      <View style={styles.historyHeader}>
        <Text style={styles.historyName}>{item.connection_name}</Text>
        <Text style={styles.historyDate}>{item.date}</Text>
      </View>
      <Text style={styles.historyCompany}>{item.company}</Text>
      <Text style={styles.historyJob}>{item.job_title}</Text>
      <View style={styles.historyStatus}>
        <View style={[styles.statusBadge, item.status === 'sent' && styles.statusSent]}>
          <Text style={styles.statusText}>{item.status}</Text>
        </View>
      </View>
    </View>
  );

  if (!linkedInConnected) {
    return (
      <View style={styles.container}>
        <View style={styles.connectContainer}>
          <Ionicons name="logo-linkedin" size={80} color="#0077b5" />
          <Text style={styles.connectTitle}>LinkedIn Profile Scraper</Text>
          <Text style={styles.connectSubtitle}>
            Sign in with LinkedIn using OpenID Connect to scrape profiles and find opportunities
          </Text>

          <TouchableOpacity
            style={styles.connectButton}
            onPress={connectLinkedIn}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="white" />
            ) : (
              <>
                <Ionicons name="logo-linkedin" size={24} color="white" />
                <Text style={styles.connectButtonText}>Sign In with LinkedIn</Text>
              </>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.connectButton, styles.refreshButton]}
            onPress={checkLinkedInStatus}
          >
            <Ionicons name="refresh" size={24} color="white" />
            <Text style={styles.connectButtonText}>Check Sign In Status</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>LinkedIn Profile Scraper</Text>
        <View style={styles.tabBar}>
          <TouchableOpacity
            style={[styles.tab, activeTab === 'connections' && styles.activeTab]}
            onPress={() => setActiveTab('connections')}
          >
            <Text style={[styles.tabText, activeTab === 'connections' && styles.activeTabText]}>
              Scraped Profiles ({connections.length})
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.tab, activeTab === 'search' && styles.activeTab]}
            onPress={() => setActiveTab('search')}
          >
            <Text style={[styles.tabText, activeTab === 'search' && styles.activeTabText]}>
              Search
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.tab, activeTab === 'history' && styles.activeTab]}
            onPress={() => setActiveTab('history')}
          >
            <Text style={[styles.tabText, activeTab === 'history' && styles.activeTabText]}>
              History ({outreachHistory.length})
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Content */}
      <ScrollView style={styles.content}>
        {activeTab === 'connections' && (
          <View>
            {loading && (
              <View style={styles.centerContainer}>
                <ActivityIndicator size="large" color="#667eea" />
                <Text style={styles.loadingText}>{scrapingStatus}</Text>
              </View>
            )}

            {!loading && scrapingStatus ? (
              <View style={styles.centerContainer}>
                <Text style={styles.statusText}>{scrapingStatus}</Text>
              </View>
            ) : null}

            {connections.length > 0 ? (
              <FlatList
                data={connections}
                renderItem={renderConnectionCard}
                keyExtractor={(item, index) => index.toString()}
                scrollEnabled={false}
              />
            ) : !loading && (
              <View style={styles.centerContainer}>
                <Ionicons name="people-outline" size={64} color="#ccc" />
                <Text style={styles.emptyText}>No scraped profiles found</Text>
                <Text style={styles.emptySubtext}>Use the search filters to find LinkedIn profiles</Text>

                <TouchableOpacity
                  style={[styles.connectButton, styles.scrapeButton]}
                  onPress={scrapeBigTechProfiles}
                >
                  <Ionicons name="business" size={24} color="white" />
                  <Text style={styles.connectButtonText}>Scrape Google Employees</Text>
                </TouchableOpacity>

                <TouchableOpacity
                  style={[styles.connectButton, styles.scrapeButton]}
                  onPress={scrapeTorontoProfessionals}
                >
                  <Ionicons name="location" size={24} color="white" />
                  <Text style={styles.connectButtonText}>Scrape Toronto Professionals</Text>
                </TouchableOpacity>
              </View>
            )}
          </View>
        )}

        {activeTab === 'search' && (
          <View style={styles.searchContainer}>
            {/* Search Header */}
            <View style={styles.searchHeader}>
              <Text style={styles.searchTitle}>Advanced LinkedIn Search</Text>
              <TouchableOpacity
                style={styles.filterToggle}
                onPress={() => setShowFilters(!showFilters)}
              >
                <Ionicons name={showFilters ? "chevron-up" : "chevron-down"} size={20} color="#667eea" />
                <Text style={styles.filterToggleText}>Filters</Text>
              </TouchableOpacity>
            </View>

            {/* Advanced Filters */}
            {showFilters && (
              <View style={styles.filtersContainer}>
                {/* Location Filter */}
                <View style={styles.filterSection}>
                  <Text style={styles.filterLabel}>📍 Location</Text>
                  <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterScroll}>
                    {locationOptions.map((location, index) => (
                      <TouchableOpacity
                        key={index}
                        style={[
                          styles.filterChip,
                          selectedLocation === location && styles.filterChipActive
                        ]}
                        onPress={() => setSelectedLocation(selectedLocation === location ? '' : location)}
                      >
                        <Text style={[
                          styles.filterChipText,
                          selectedLocation === location && styles.filterChipTextActive
                        ]}>
                          {location.split(',')[0]}
                        </Text>
                      </TouchableOpacity>
                    ))}
                  </ScrollView>
                </View>

                {/* Company Filter */}
                <View style={styles.filterSection}>
                  <Text style={styles.filterLabel}>🏢 Company</Text>
                  <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterScroll}>
                    {companyOptions.map((company, index) => (
                      <TouchableOpacity
                        key={index}
                        style={[
                          styles.filterChip,
                          selectedCompany === company && styles.filterChipActive
                        ]}
                        onPress={() => setSelectedCompany(selectedCompany === company ? '' : company)}
                      >
                        <Text style={[
                          styles.filterChipText,
                          selectedCompany === company && styles.filterChipTextActive
                        ]}>
                          {company}
                        </Text>
                      </TouchableOpacity>
                    ))}
                  </ScrollView>
                </View>

                {/* Job Title Filter */}
                <View style={styles.filterSection}>
                  <Text style={styles.filterLabel}>💼 Job Title</Text>
                  <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterScroll}>
                    {jobTitleOptions.map((title, index) => (
                      <TouchableOpacity
                        key={index}
                        style={[
                          styles.filterChip,
                          selectedJobTitle === title && styles.filterChipActive
                        ]}
                        onPress={() => setSelectedJobTitle(selectedJobTitle === title ? '' : title)}
                      >
                        <Text style={[
                          styles.filterChipText,
                          selectedJobTitle === title && styles.filterChipTextActive
                        ]}>
                          {title}
                        </Text>
                      </TouchableOpacity>
                    ))}
                  </ScrollView>
                </View>

                {/* Alumni Filter */}
                <View style={styles.filterSection}>
                  <TouchableOpacity
                    style={styles.alumniToggle}
                    onPress={() => setAlumniOnly(!alumniOnly)}
                  >
                    <View style={[styles.checkbox, alumniOnly && styles.checkboxActive]}>
                      {alumniOnly && <Ionicons name="checkmark" size={16} color="white" />}
                    </View>
                    <Text style={styles.alumniText}>🎓 Alumni Only</Text>
                  </TouchableOpacity>
                </View>

                {/* Clear Filters */}
                <TouchableOpacity
                  style={styles.clearFiltersButton}
                  onPress={() => {
                    setSelectedLocation('');
                    setSelectedCompany('');
                    setSelectedJobTitle('');
                    setSelectedUniversity('');
                    setAlumniOnly(false);
                  }}
                >
                  <Ionicons name="refresh" size={16} color="#667eea" />
                  <Text style={styles.clearFiltersText}>Clear All Filters</Text>
                </TouchableOpacity>
              </View>
            )}

            {/* Search Input */}
            <View style={styles.searchInputContainer}>
              <TextInput
                style={styles.searchInput}
                placeholder="Search by name, company, or keywords..."
                value={searchQuery}
                onChangeText={setSearchQuery}
                onSubmitEditing={searchProfiles}
              />
              <TouchableOpacity
                style={styles.searchButton}
                onPress={searchProfiles}
                disabled={searchLoading}
              >
                {searchLoading ? (
                  <ActivityIndicator size="small" color="white" />
                ) : (
                  <Ionicons name="search" size={20} color="white" />
                )}
              </TouchableOpacity>
            </View>

            {/* Status Message */}
            {searchLoading && (
              <View style={styles.centerContainer}>
                <ActivityIndicator size="large" color="#667eea" />
                <Text style={styles.loadingText}>{scrapingStatus}</Text>
              </View>
            )}

            {scrapingStatus && !searchLoading && (
              <View style={styles.centerContainer}>
                <Text style={styles.statusText}>{scrapingStatus}</Text>
              </View>
            )}

            {/* Search Results */}
            {!searchLoading && searchResults.length > 0 && (
              <View style={styles.resultsHeader}>
                <Text style={styles.resultsCount}>{searchResults.length} profiles found</Text>
                <TouchableOpacity
                  style={styles.clearResultsButton}
                  onPress={() => setSearchResults([])}
                >
                  <Ionicons name="close" size={16} color="#666" />
                </TouchableOpacity>
              </View>
            )}

            {!searchLoading && searchResults.length > 0 && (
              <FlatList
                data={searchResults}
                renderItem={renderConnectionCard}
                keyExtractor={(item, index) => `search-${index}`}
                scrollEnabled={false}
              />
            )}

            {/* Empty State */}
            {!searchLoading && searchResults.length === 0 && !scrapingStatus && (
              <View style={styles.emptySearchContainer}>
                <Ionicons name="search-outline" size={64} color="#ccc" />
                <Text style={styles.emptySearchText}>Search for LinkedIn professionals</Text>
                <Text style={styles.emptySearchSubtext}>Use filters to find specific profiles</Text>
              </View>
            )}
          </View>
        )}

        {activeTab === 'history' && (
          <View>
            {outreachHistory.length > 0 ? (
              <FlatList
                data={outreachHistory}
                renderItem={renderOutreachHistoryItem}
                keyExtractor={(item, index) => `history-${index}`}
                scrollEnabled={false}
              />
            ) : (
              <View style={styles.centerContainer}>
                <Ionicons name="mail-outline" size={64} color="#ccc" />
                <Text style={styles.emptyText}>No outreach history</Text>
                <Text style={styles.emptySubtext}>Your sent messages will appear here</Text>
              </View>
            )}
          </View>
        )}
      </ScrollView>

      {/* Email Modal */}
      {selectedConnection && (
        <View style={styles.modalOverlay}>
          <View style={styles.modal}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Message {selectedConnection.name}</Text>
              <TouchableOpacity onPress={() => setSelectedConnection(null)}>
                <Ionicons name="close" size={24} color="#666" />
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.modalContent}>
              <TextInput
                style={styles.emailInput}
                placeholder="Your message will be generated here..."
                value={emailContent}
                onChangeText={setEmailContent}
                multiline
                numberOfLines={8}
              />
            </ScrollView>

            <View style={styles.modalActions}>
              <TouchableOpacity
                style={[styles.modalButton, styles.sendButton]}
                onPress={sendOutreach}
                disabled={sendingEmail}
              >
                {sendingEmail ? (
                  <ActivityIndicator size="small" color="white" />
                ) : (
                  <Text style={styles.sendButtonText}>Send Message</Text>
                )}
              </TouchableOpacity>
            </View>
          </View>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  connectContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  connectTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 20,
    marginBottom: 10,
  },
  connectSubtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 30,
  },
  connectButton: {
    backgroundColor: '#0077b5',
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 25,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    marginBottom: 15,
  },
  refreshButton: {
    backgroundColor: '#667eea',
  },
  scrapeButton: {
    backgroundColor: '#51cf66',
    marginTop: 10,
  },
  searchHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  searchTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  filterToggle: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 15,
    paddingVertical: 8,
    backgroundColor: '#f0f8ff',
    borderRadius: 20,
  },
  filterToggleText: {
    fontSize: 14,
    color: '#667eea',
    fontWeight: '600',
    marginLeft: 5,
  },
  filtersContainer: {
    backgroundColor: 'white',
    borderRadius: 15,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  filterSection: {
    marginBottom: 20,
  },
  filterLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  filterScroll: {
    flexDirection: 'row',
  },
  filterChip: {
    paddingHorizontal: 15,
    paddingVertical: 8,
    backgroundColor: '#f8f9fa',
    borderRadius: 20,
    marginRight: 10,
    borderWidth: 1,
    borderColor: '#e9ecef',
  },
  filterChipActive: {
    backgroundColor: '#667eea',
    borderColor: '#667eea',
  },
  filterChipText: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
  },
  filterChipTextActive: {
    color: 'white',
    fontWeight: 'bold',
  },
  alumniToggle: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  checkbox: {
    width: 20,
    height: 20,
    borderRadius: 4,
    borderWidth: 2,
    borderColor: '#ddd',
    marginRight: 10,
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkboxActive: {
    backgroundColor: '#667eea',
    borderColor: '#667eea',
  },
  alumniText: {
    fontSize: 16,
    color: '#333',
    fontWeight: '500',
  },
  clearFiltersButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    backgroundColor: '#f8f9fa',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#e9ecef',
  },
  clearFiltersText: {
    fontSize: 14,
    color: '#667eea',
    fontWeight: '600',
    marginLeft: 5,
  },
  resultsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
    paddingHorizontal: 5,
  },
  resultsCount: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  clearResultsButton: {
    padding: 5,
  },
  emptySearchContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptySearchText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 10,
    textAlign: 'center',
  },
  emptySearchSubtext: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginTop: 5,
  },
  connectButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 10,
  },
  header: {
    padding: 20,
    paddingBottom: 10,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: 20,
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: 'white',
    borderRadius: 25,
    padding: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  tab: {
    flex: 1,
    paddingVertical: 10,
    paddingHorizontal: 15,
    borderRadius: 20,
    alignItems: 'center',
  },
  activeTab: {
    backgroundColor: '#667eea',
  },
  tabText: {
    fontSize: 14,
    color: '#666',
    fontWeight: '600',
  },
  activeTabText: {
    color: 'white',
    fontWeight: 'bold',
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  centerContainer: {
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
  },
  statusText: {
    fontSize: 16,
    color: '#51cf66',
    fontWeight: '600',
    textAlign: 'center',
    marginTop: 10,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 10,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginTop: 5,
    marginBottom: 20,
  },
  searchContainer: {
    paddingTop: 20,
  },
  searchInputContainer: {
    flexDirection: 'row',
    marginBottom: 20,
  },
  searchInput: {
    flex: 1,
    backgroundColor: 'white',
    borderRadius: 25,
    paddingHorizontal: 20,
    paddingVertical: 15,
    fontSize: 16,
    marginRight: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  searchButton: {
    backgroundColor: '#667eea',
    width: 50,
    height: 50,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  connectionCard: {
    backgroundColor: 'white',
    borderRadius: 15,
    padding: 20,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  connectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  connectionAvatar: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#667eea',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  avatarText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: 'white',
  },
  connectionInfo: {
    flex: 1,
  },
  connectionName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  connectionTitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  connectionCompany: {
    fontSize: 14,
    color: '#667eea',
    fontWeight: '600',
    marginTop: 2,
  },
  alumniBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f0f8ff',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  alumniText: {
    fontSize: 12,
    color: '#667eea',
    fontWeight: '600',
    marginLeft: 4,
  },
  connectionMeta: {
    flexDirection: 'row',
    marginBottom: 15,
    flexWrap: 'wrap',
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 20,
    marginBottom: 5,
  },
  metaText: {
    fontSize: 14,
    color: '#666',
    marginLeft: 5,
  },
  connectionActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
    flex: 1,
    marginHorizontal: 5,
    justifyContent: 'center',
  },
  messageButton: {
    backgroundColor: '#f0f8ff',
    borderWidth: 1,
    borderColor: '#667eea',
  },
  viewButton: {
    backgroundColor: '#f0fff0',
    borderWidth: 1,
    borderColor: '#51cf66',
  },
  actionButtonText: {
    fontSize: 14,
    fontWeight: '600',
    marginLeft: 5,
  },
  historyCard: {
    backgroundColor: 'white',
    borderRadius: 15,
    padding: 20,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  historyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  historyName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  historyDate: {
    fontSize: 14,
    color: '#666',
  },
  historyCompany: {
    fontSize: 14,
    color: '#667eea',
    fontWeight: '600',
    marginBottom: 5,
  },
  historyJob: {
    fontSize: 14,
    color: '#666',
    marginBottom: 10,
  },
  historyStatus: {
    flexDirection: 'row',
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 12,
    backgroundColor: '#f0f0f0',
  },
  statusSent: {
    backgroundColor: '#e8f5e8',
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#666',
  },
  modalOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  modal: {
    backgroundColor: 'white',
    borderRadius: 20,
    padding: 20,
    margin: 20,
    width: width - 40,
    maxHeight: height * 0.8,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  modalContent: {
    flex: 1,
    marginBottom: 20,
  },
  emailInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 10,
    padding: 15,
    fontSize: 16,
    textAlignVertical: 'top',
    minHeight: 150,
  },
  modalActions: {
    flexDirection: 'row',
  },
  modalButton: {
    flex: 1,
    paddingVertical: 15,
    borderRadius: 25,
  },
  sendButton: {
    backgroundColor: '#667eea',
  },
  sendButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
});

export default RecruiterNetwork;