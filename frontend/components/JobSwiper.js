import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  Dimensions,
  Animated,
  Image
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { API_URL } from '../config';

const { width, height } = Dimensions.get('window');

const JobSwiper = ({ onSaveJob, onApplyJob }) => {
  const [jobs, setJobs] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showJobModal, setShowJobModal] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_URL}/jobs`);

      if (!response.ok) {
        throw new Error(`Server returned ${response.status} status`);
      }

      const data = await response.json();
      setJobs(data);
    } catch (err) {
      console.error('Fetch error:', err);
      setError(`Failed to load jobs: ${err.message || 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const openJobModal = (job) => {
    setSelectedJob(job);
    setShowJobModal(true);
  };

  const closeJobModal = () => {
    setShowJobModal(false);
    setSelectedJob(null);
  };

  const handleSaveJob = (job) => {
    onSaveJob(job);
    Alert.alert('Job Saved', `${job.title} has been saved to your list!`);
  };

  const handleSwipe = async (index, direction) => {
    if (index >= jobs.length) return;

    const job = jobs[index];

    if (direction === 'right') {
      // Like - Save job and potentially auto-apply
      handleSaveJob(job);
      Alert.alert(
        'Job Liked! 💚',
        `Saved ${job.title} at ${job.company}`,
        [
          { text: 'Apply Now', onPress: () => onApplyJob(job) },
          { text: 'Later', style: 'cancel' }
        ]
      );
    } else if (direction === 'left') {
      // Dislike - Skip job
      Alert.alert('Job Skipped', `Skipped ${job.title} at ${job.company}`);
    }

    // Move to next job
    setCurrentIndex(prev => prev + 1);
  };

  const renderCard = (job, index) => {
    if (index < currentIndex) return null;

    return (
      <View
        key={job.id}
        style={[
          styles.card,
          { zIndex: jobs.length - index }
        ]}
      >
        <View style={styles.cardHeader}>
          <View style={styles.companyInfo}>
            <View style={styles.companyLogo}>
              <Text style={styles.companyInitial}>
                {job.company.charAt(0).toUpperCase()}
              </Text>
            </View>
            <View style={styles.companyDetails}>
              <Text style={styles.companyName}>{job.company}</Text>
              <Text style={styles.jobLocation}>{job.location}</Text>
            </View>
          </View>
          <TouchableOpacity
            style={styles.infoButton}
            onPress={() => openJobModal(job)}
          >
            <Ionicons name="information-circle-outline" size={24} color="#667eea" />
          </TouchableOpacity>
        </View>

        <View style={styles.cardContent}>
          <Text style={styles.jobTitle}>{job.title}</Text>
          <Text style={styles.jobDescription} numberOfLines={4}>
            {job.description}
          </Text>

          <View style={styles.jobMeta}>
            <View style={styles.metaItem}>
              <Ionicons name="time-outline" size={16} color="#666" />
              <Text style={styles.metaText}>
                {job.posted_at ? new Date(job.posted_at).toLocaleDateString() : 'Recently'}
              </Text>
            </View>
            <View style={styles.metaItem}>
              <Ionicons name="business-outline" size={16} color="#666" />
              <Text style={styles.metaText}>{job.source || 'Job Board'}</Text>
            </View>
          </View>
        </View>

        <View style={styles.cardFooter}>
          <TouchableOpacity
            style={[styles.actionButton, styles.dislikeButton]}
            onPress={() => handleSwipe(currentIndex, 'left')}
          >
            <Ionicons name="close" size={30} color="#ff6b6b" />
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionButton, styles.infoButton]}
            onPress={() => openJobModal(job)}
          >
            <Ionicons name="information-circle" size={30} color="#667eea" />
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.actionButton, styles.likeButton]}
            onPress={() => handleSwipe(currentIndex, 'right')}
          >
            <Ionicons name="heart" size={30} color="#51cf66" />
          </TouchableOpacity>
        </View>
      </View>
    );
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#667eea" />
        <Text style={styles.loadingText}>Loading jobs...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.centerContainer}>
        <Ionicons name="alert-circle-outline" size={64} color="#ff6b6b" />
        <Text style={styles.errorText}>❌ {error}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={fetchJobs}>
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (currentIndex >= jobs.length) {
    return (
      <View style={styles.centerContainer}>
        <Ionicons name="checkmark-circle-outline" size={64} color="#51cf66" />
        <Text style={styles.emptyText}>You've seen all jobs!</Text>
        <Text style={styles.emptySubtext}>Check back later for new opportunities</Text>
        <TouchableOpacity style={styles.retryButton} onPress={() => {
          setCurrentIndex(0);
          fetchJobs();
        }}>
          <Text style={styles.retryButtonText}>Refresh Jobs</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Swipe Jobs</Text>
        <Text style={styles.headerSubtitle}>
          {currentIndex + 1} of {jobs.length} jobs
        </Text>
      </View>

      <View style={styles.cardsContainer}>
        <View style={styles.cardWrapper}>
          {jobs.map((job, index) => renderCard(job, index))}
        </View>
      </View>

      {/* Job Modal */}
      {showJobModal && selectedJob && (
        <View style={styles.modalOverlay}>
          <View style={styles.modal}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>{selectedJob.title}</Text>
              <TouchableOpacity onPress={closeJobModal} style={styles.closeButton}>
                <Ionicons name="close" size={24} color="#666" />
              </TouchableOpacity>
            </View>

            <View style={styles.modalContent}>
              <Text style={styles.modalCompany}>{selectedJob.company}</Text>
              <Text style={styles.modalLocation}>{selectedJob.location}</Text>
              <Text style={styles.modalDescription}>{selectedJob.description}</Text>
            </View>

            <View style={styles.modalActions}>
              <TouchableOpacity
                style={[styles.modalButton, styles.applyButton]}
                onPress={() => {
                  onApplyJob(selectedJob);
                  closeJobModal();
                }}
              >
                <Text style={styles.applyButtonText}>Apply Now</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.modalButton, styles.saveButton]}
                onPress={() => {
                  handleSaveJob(selectedJob);
                  closeJobModal();
                }}
              >
                <Text style={styles.saveButtonText}>Save Job</Text>
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
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
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
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginTop: 5,
  },
  cardsContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  cardWrapper: {
    width: width - 40,
    height: height * 0.6,
    position: 'relative',
  },
  card: {
    position: 'absolute',
    width: '100%',
    height: '100%',
    backgroundColor: 'white',
    borderRadius: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 8,
    padding: 20,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  companyInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  companyLogo: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#667eea',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  companyInitial: {
    fontSize: 20,
    fontWeight: 'bold',
    color: 'white',
  },
  companyDetails: {
    flex: 1,
  },
  companyName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  jobLocation: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  cardContent: {
    flex: 1,
  },
  jobTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
    lineHeight: 28,
  },
  jobDescription: {
    fontSize: 16,
    color: '#666',
    lineHeight: 24,
    marginBottom: 20,
  },
  jobMeta: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  metaText: {
    fontSize: 14,
    color: '#666',
    marginLeft: 5,
  },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    paddingTop: 20,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  actionButton: {
    width: 60,
    height: 60,
    borderRadius: 30,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  dislikeButton: {
    backgroundColor: 'white',
    borderWidth: 2,
    borderColor: '#ff6b6b',
  },
  likeButton: {
    backgroundColor: 'white',
    borderWidth: 2,
    borderColor: '#51cf66',
  },
  infoButton: {
    backgroundColor: 'white',
    borderWidth: 2,
    borderColor: '#667eea',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  errorText: {
    fontSize: 18,
    color: '#ff6b6b',
    textAlign: 'center',
    marginTop: 10,
  },
  emptyText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginTop: 10,
  },
  emptySubtext: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginTop: 5,
  },
  retryButton: {
    backgroundColor: '#667eea',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 25,
    marginTop: 20,
  },
  retryButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
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
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  closeButton: {
    padding: 5,
  },
  modalContent: {
    flex: 1,
  },
  modalCompany: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#667eea',
    marginBottom: 5,
  },
  modalLocation: {
    fontSize: 14,
    color: '#666',
    marginBottom: 15,
  },
  modalDescription: {
    fontSize: 16,
    color: '#333',
    lineHeight: 24,
  },
  modalActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 20,
  },
  modalButton: {
    flex: 1,
    paddingVertical: 15,
    borderRadius: 25,
    marginHorizontal: 5,
  },
  applyButton: {
    backgroundColor: '#51cf66',
  },
  saveButton: {
    backgroundColor: '#667eea',
  },
  applyButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  saveButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
});

export default JobSwiper;