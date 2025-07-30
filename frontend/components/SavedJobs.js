import React, { useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    FlatList,
    TouchableOpacity,
    Modal,
    TextInput,
    Linking,
    Alert,
    ActivityIndicator
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';

const SavedJobs = ({ jobs, onClose, onRemoveJob, onApplyJob }) => {
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedJob, setSelectedJob] = useState(null);
    const [showJobModal, setShowJobModal] = useState(false);
    const [applying, setApplying] = useState(false);

    const filteredJobs = jobs.filter(job =>
        job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        job.company.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const handleRemoveJob = (jobId) => {
        Alert.alert(
            'Remove Job',
            'Are you sure you want to remove this job from your saved list?',
            [
                { text: 'Cancel', style: 'cancel' },
                { text: 'Remove', style: 'destructive', onPress: () => onRemoveJob(jobId) }
            ]
        );
    };

    const handleApplyJob = async (job) => {
        setApplying(true);
        try {
            if (onApplyJob) {
                await onApplyJob(job);
            }
            Alert.alert('Success', 'Application submitted!');
        } catch (error) {
            Alert.alert('Error', 'Failed to apply. Please try again.');
        } finally {
            setApplying(false);
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

    const renderJobCard = ({ item }) => (
        <LinearGradient
            colors={['#f8fafc', '#f1f8ff']}
            style={styles.jobCard}
        >
            <View style={styles.jobHeader}>
                <View style={styles.jobInfo}>
                    <Text style={styles.jobTitle}>{item.title}</Text>
                    <Text style={styles.jobCompany}>{item.company}</Text>
                    <Text style={styles.jobLocation}>{item.location}</Text>
                    <Text style={styles.jobDate}>
                        Posted: {new Date(item.posted_at).toLocaleDateString()}
                    </Text>
                </View>
                <View style={styles.jobActions}>
                    <TouchableOpacity
                        style={styles.actionButton}
                        onPress={() => openJobModal(item)}
                    >
                        <Ionicons name="information-circle-outline" size={24} color="#1e88e5" />
                    </TouchableOpacity>
                    <TouchableOpacity
                        style={styles.actionButton}
                        onPress={() => handleRemoveJob(item.id)}
                    >
                        <Ionicons name="trash-outline" size={24} color="#f44336" />
                    </TouchableOpacity>
                </View>
            </View>
            <View style={styles.jobDescription}>
                <Text style={styles.descriptionText} numberOfLines={3}>
                    {item.description}
                </Text>
            </View>
            <View style={styles.jobButtons}>
                <TouchableOpacity
                    style={styles.applyButton}
                    onPress={() => handleApplyJob(item)}
                    disabled={applying}
                >
                    {applying ? (
                        <ActivityIndicator size="small" color="#fff" />
                    ) : (
                        <>
                            <Ionicons name="send" size={16} color="#fff" />
                            <Text style={styles.applyButtonText}>Apply</Text>
                        </>
                    )}
                </TouchableOpacity>
                <TouchableOpacity
                    style={styles.viewButton}
                    onPress={() => Linking.openURL(item.url)}
                >
                    <Ionicons name="open-outline" size={16} color="#1e88e5" />
                    <Text style={styles.viewButtonText}>View Details</Text>
                </TouchableOpacity>
            </View>
        </LinearGradient>
    );

    const renderEmptyState = () => (
        <View style={styles.emptyContainer}>
            <Ionicons name="bookmark-outline" size={64} color="#ccc" />
            <Text style={styles.emptyTitle}>No Saved Jobs</Text>
            <Text style={styles.emptyText}>
                Jobs you save will appear here for easy access
            </Text>
        </View>
    );

    return (
        <View style={styles.container}>
            <LinearGradient
                colors={['#e3ffe6', '#e0f7fa']}
                style={styles.header}
            >
                <View style={styles.headerContent}>
                    <TouchableOpacity style={styles.closeButton} onPress={onClose}>
                        <Ionicons name="close" size={24} color="#1a237e" />
                    </TouchableOpacity>
                    <Text style={styles.headerTitle}>Saved Jobs</Text>
                    <View style={styles.headerSpacer} />
                </View>
                <View style={styles.searchContainer}>
                    <Ionicons name="search" size={20} color="#888" style={styles.searchIcon} />
                    <TextInput
                        style={styles.searchInput}
                        placeholder="Search saved jobs..."
                        value={searchQuery}
                        onChangeText={setSearchQuery}
                        placeholderTextColor="#aaa"
                    />
                </View>
            </LinearGradient>

            <FlatList
                data={filteredJobs}
                renderItem={renderJobCard}
                keyExtractor={(item) => item.id.toString()}
                contentContainerStyle={styles.list}
                ListEmptyComponent={renderEmptyState()}
                showsVerticalScrollIndicator={false}
            />

            <Modal
                visible={showJobModal}
                transparent
                animationType="slide"
                onRequestClose={closeJobModal}
            >
                <View style={styles.modalOverlay}>
                    <View style={styles.jobModalContent}>
                        {selectedJob && (
                            <>
                                <Text style={styles.modalTitle}>{selectedJob.title}</Text>
                                <Text style={styles.modalCompany}>{selectedJob.company}</Text>
                                <Text style={styles.modalLocation}>{selectedJob.location}</Text>
                                <Text style={styles.modalDate}>
                                    Posted: {new Date(selectedJob.posted_at).toLocaleDateString()}
                                </Text>
                                <Text style={styles.modalDescription}>{selectedJob.description}</Text>
                                <View style={styles.modalButtons}>
                                    <TouchableOpacity
                                        style={styles.modalApplyButton}
                                        onPress={() => {
                                            closeJobModal();
                                            handleApplyJob(selectedJob);
                                        }}
                                    >
                                        <Ionicons name="send" size={16} color="#fff" />
                                        <Text style={styles.modalApplyButtonText}>Apply Now</Text>
                                    </TouchableOpacity>
                                    <TouchableOpacity
                                        style={styles.modalViewButton}
                                        onPress={() => Linking.openURL(selectedJob.url)}
                                    >
                                        <Ionicons name="open-outline" size={16} color="#1e88e5" />
                                        <Text style={styles.modalViewButtonText}>View on Site</Text>
                                    </TouchableOpacity>
                                </View>
                                <TouchableOpacity style={styles.modalCloseButton} onPress={closeJobModal}>
                                    <Text style={styles.modalCloseButtonText}>Close</Text>
                                </TouchableOpacity>
                            </>
                        )}
                    </View>
                </View>
            </Modal>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
    },
    header: {
        paddingTop: 50,
        paddingBottom: 20,
        paddingHorizontal: 16,
        borderBottomLeftRadius: 24,
        borderBottomRightRadius: 24,
        elevation: 4,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 8,
    },
    headerContent: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 16,
    },
    closeButton: {
        padding: 8,
    },
    headerTitle: {
        flex: 1,
        fontSize: 24,
        fontWeight: 'bold',
        color: '#1a237e',
        textAlign: 'center',
    },
    headerSpacer: {
        width: 40,
    },
    searchContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#fff',
        borderRadius: 20,
        paddingHorizontal: 12,
        paddingVertical: 8,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.05,
        shadowRadius: 4,
        elevation: 2,
    },
    searchIcon: {
        marginRight: 8,
    },
    searchInput: {
        flex: 1,
        fontSize: 16,
        color: '#333',
    },
    list: {
        padding: 16,
    },
    jobCard: {
        borderRadius: 16,
        marginBottom: 16,
        padding: 20,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.1,
        shadowRadius: 8,
        elevation: 4,
    },
    jobHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: 12,
    },
    jobInfo: {
        flex: 1,
    },
    jobTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#1a237e',
        marginBottom: 4,
    },
    jobCompany: {
        fontSize: 16,
        color: '#333',
        marginBottom: 2,
    },
    jobLocation: {
        fontSize: 14,
        color: '#666',
        marginBottom: 4,
    },
    jobDate: {
        fontSize: 12,
        color: '#999',
        fontStyle: 'italic',
    },
    jobActions: {
        flexDirection: 'row',
        gap: 8,
    },
    actionButton: {
        padding: 4,
    },
    jobDescription: {
        marginBottom: 16,
    },
    descriptionText: {
        fontSize: 14,
        color: '#555',
        lineHeight: 20,
    },
    jobButtons: {
        flexDirection: 'row',
        gap: 12,
    },
    applyButton: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#43cea2',
        borderRadius: 8,
        paddingVertical: 10,
        paddingHorizontal: 16,
        flex: 1,
        justifyContent: 'center',
    },
    applyButtonText: {
        color: '#fff',
        fontWeight: 'bold',
        marginLeft: 6,
    },
    viewButton: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#fff',
        borderRadius: 8,
        paddingVertical: 10,
        paddingHorizontal: 16,
        borderWidth: 1,
        borderColor: '#1e88e5',
    },
    viewButtonText: {
        color: '#1e88e5',
        fontWeight: 'bold',
        marginLeft: 6,
    },
    emptyContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 40,
    },
    emptyTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        color: '#666',
        marginTop: 16,
        marginBottom: 8,
    },
    emptyText: {
        fontSize: 16,
        color: '#999',
        textAlign: 'center',
        lineHeight: 24,
    },
    modalOverlay: {
        flex: 1,
        backgroundColor: 'rgba(0,0,0,0.5)',
        justifyContent: 'center',
        alignItems: 'center',
    },
    jobModalContent: {
        backgroundColor: '#fff',
        borderRadius: 20,
        padding: 24,
        width: '90%',
        maxHeight: '80%',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.2,
        shadowRadius: 12,
        elevation: 8,
    },
    modalTitle: {
        fontSize: 22,
        fontWeight: 'bold',
        color: '#1a237e',
        marginBottom: 8,
        textAlign: 'center',
    },
    modalCompany: {
        fontSize: 18,
        fontWeight: '600',
        color: '#333',
        marginBottom: 4,
        textAlign: 'center',
    },
    modalLocation: {
        fontSize: 16,
        color: '#666',
        marginBottom: 8,
        textAlign: 'center',
    },
    modalDate: {
        fontSize: 14,
        color: '#999',
        marginBottom: 16,
        textAlign: 'center',
        fontStyle: 'italic',
    },
    modalDescription: {
        fontSize: 16,
        color: '#444',
        lineHeight: 24,
        marginBottom: 24,
    },
    modalButtons: {
        flexDirection: 'row',
        gap: 12,
        marginBottom: 16,
    },
    modalApplyButton: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#43cea2',
        borderRadius: 8,
        paddingVertical: 12,
        paddingHorizontal: 20,
        flex: 1,
        justifyContent: 'center',
    },
    modalApplyButtonText: {
        color: '#fff',
        fontWeight: 'bold',
        marginLeft: 6,
    },
    modalViewButton: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#fff',
        borderRadius: 8,
        paddingVertical: 12,
        paddingHorizontal: 20,
        borderWidth: 1,
        borderColor: '#1e88e5',
        flex: 1,
        justifyContent: 'center',
    },
    modalViewButtonText: {
        color: '#1e88e5',
        fontWeight: 'bold',
        marginLeft: 6,
    },
    modalCloseButton: {
        backgroundColor: '#f5f5f5',
        borderRadius: 8,
        paddingVertical: 12,
        alignItems: 'center',
    },
    modalCloseButtonText: {
        color: '#666',
        fontWeight: '600',
    },
});

export default SavedJobs; 