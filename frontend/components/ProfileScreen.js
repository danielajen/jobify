import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  ActivityIndicator,
  Switch,
  Modal
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import * as DocumentPicker from 'expo-document-picker';
import { useUser } from '../context/UserContext';
import { API_URL } from '../config';

const ProfileScreen = () => {
  // Simplified state structure to reduce property count
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [graduationYear, setGraduationYear] = useState('');
  const [degree, setDegree] = useState('');
  const [resume, setResume] = useState('');
  const [strengths, setStrengths] = useState('');
  const [whyCompany, setWhyCompany] = useState('');
  const [jobAlerts, setJobAlerts] = useState(true);
  const [autoApply, setAutoApply] = useState(true);

  const [saving, setSaving] = useState(false);
  const [uploadingResume, setUploadingResume] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showResumeModal, setShowResumeModal] = useState(false);
  const { user, updateUser } = useUser();

  useEffect(() => {
    if (user) {
      setName(user.name || '');
      setEmail(user.email || '');
      setPhone(user.phone || '');
      setGraduationYear(user.graduation_year || '');
      setDegree(user.degree || '');
      setResume(user.resume || '');
      setStrengths(user.answers?.strengths || '');
      setWhyCompany(user.answers?.why_company || '');
      setJobAlerts(user.job_alerts !== false);
      setAutoApply(user.auto_apply !== false);

      // Clear any previous messages when user data loads
      clearMessages();
    }
  }, [user]);

  const clearMessages = () => {
    setError(null);
    setSuccess(null);
  };

  const handleSaveProfile = async () => {
    setSaving(true);
    clearMessages();

    try {
      const profileData = {
        user_id: user.id,
        name,
        email,
        phone,
        graduation_year: graduationYear,
        degree,
        resume,
        answers: { strengths, why_company: whyCompany },
        job_alerts: jobAlerts,
        auto_apply: autoApply
      };

      const response = await fetch(`${API_URL}/profile`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profileData)
      });

      if (!response.ok) {
        const data = await response.json();
        setError(data.error || 'Failed to save profile.');
        return;
      }

      setSuccess('Profile saved successfully!');
      updateUser(profileData);
    } catch (err) {
      setError('Network error: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleAttachResume = async () => {
    try {
      setUploadingResume(true);
      const result = await DocumentPicker.getDocumentAsync({
        type: ['application/pdf', 'application/msword',
          'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
        copyToCacheDirectory: true
      });

      if (result.type === 'success') {
        const uploadUrl = `${API_URL}/upload-resume`;

        const form = new FormData();
        form.append('resume', {
          uri: result.uri,
          name: result.name,
          type: result.mimeType
        });
        form.append('user_id', user.id);

        const response = await fetch(uploadUrl, {
          method: 'POST',
          body: form,
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || `Upload failed: ${response.status}`);
        }

        const data = await response.json();

        // Update local state with the saved resume filename
        setResume(data.resume_path);

        // Update the user context with the new resume path
        const updatedUser = { ...user, resume: data.resume_path };
        updateUser(updatedUser);

        setSuccess('Resume uploaded and saved successfully!');
      }
    } catch (err) {
      console.error('Resume upload error:', err);
      setError('Upload Error: ' + err.message);
    } finally {
      setUploadingResume(false);
    }
  };

  const getResumeFileName = () => {
    if (!resume) return null;
    // Handle both full paths and just filenames
    const fileName = resume.includes('/') ? resume.split('/').pop() : resume;
    return fileName || 'Resume.pdf';
  };

  const renderField = (label, value, onChangeText, placeholder, keyboardType = 'default', multiline = false) => (
    <View style={styles.fieldContainer}>
      <Text style={styles.fieldLabel}>{label}</Text>
      <TextInput
        style={[styles.textInput, multiline && styles.textArea]}
        value={value}
        onChangeText={onChangeText}
        placeholder={placeholder}
        keyboardType={keyboardType}
        multiline={multiline}
        numberOfLines={multiline ? 3 : 1}
      />
    </View>
  );

  const renderResumeBox = () => (
    <LinearGradient
      colors={resume ? ['#e8f5e9', '#c8e6c9'] : ['#fff3e0', '#ffe0b2']}
      style={styles.resumeBox}
    >
      <View style={styles.resumeHeader}>
        <Ionicons
          name={resume ? "document-text" : "document-outline"}
          size={24}
          color={resume ? "#2e7d32" : "#f57c00"}
        />
        <Text style={styles.resumeTitle}>
          {resume ? 'Resume Saved' : 'No Resume Attached'}
        </Text>
      </View>

      {resume ? (
        <View style={styles.resumeContent}>
          <Text style={styles.resumeFileName}>{getResumeFileName()}</Text>
          <Text style={styles.resumeStatus}>✅ Successfully uploaded and saved</Text>
          <View style={styles.resumeActions}>
            <TouchableOpacity
              style={styles.resumeActionButton}
              onPress={() => setShowResumeModal(true)}
            >
              <Ionicons name="eye-outline" size={16} color="#1e88e5" />
              <Text style={styles.resumeActionText}>View</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.resumeActionButton}
              onPress={handleAttachResume}
            >
              <Ionicons name="refresh-outline" size={16} color="#ff9800" />
              <Text style={styles.resumeActionText}>Replace</Text>
            </TouchableOpacity>
          </View>
        </View>
      ) : (
        <TouchableOpacity
          style={styles.attachResumeButton}
          onPress={handleAttachResume}
          disabled={uploadingResume}
        >
          {uploadingResume ? (
            <ActivityIndicator size="small" color="#fff" />
          ) : (
            <>
              <Ionicons name="cloud-upload-outline" size={20} color="#fff" />
              <Text style={styles.attachResumeText}>Attach Resume</Text>
            </>
          )}
        </TouchableOpacity>
      )}
    </LinearGradient>
  );

  if (!user) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#1e88e5" />
        <Text style={styles.loadingText}>Loading user profile...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <LinearGradient
        colors={['#e3ffe6', '#e0f7fa']}
        style={styles.header}
      >
        <Text style={styles.headerTitle}>Profile</Text>
        <Text style={styles.headerSubtitle}>Manage your application settings</Text>
      </LinearGradient>

      <View style={styles.content}>
        {renderResumeBox()}

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Personal Information</Text>
          {renderField('Full Name', name, setName, 'Enter your full name')}
          {renderField('Email', email, setEmail, 'Enter your email', 'email-address')}
          {renderField('Phone', phone, setPhone, 'Enter your phone number', 'phone-pad')}
          {renderField('Graduation Year', graduationYear, setGraduationYear, 'e.g., 2026')}
          {renderField('Degree', degree, setDegree, 'e.g., Computer Science', 'default', true)}
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Application Answers</Text>
          {renderField('Key Strengths', strengths, setStrengths, 'Describe your key strengths and skills...', 'default', true)}
          {renderField('Why This Company', whyCompany, setWhyCompany, 'Why are you interested in this company?', 'default', true)}
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Application Settings</Text>
          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Job Alerts</Text>
              <Text style={styles.settingDescription}>Receive notifications for new opportunities</Text>
            </View>
            <Switch
              value={jobAlerts}
              onValueChange={setJobAlerts}
              trackColor={{ false: '#e0e0e0', true: '#43cea2' }}
              thumbColor={jobAlerts ? '#fff' : '#f4f3f4'}
            />
          </View>
          <View style={styles.settingRow}>
            <View style={styles.settingInfo}>
              <Text style={styles.settingLabel}>Auto-Apply</Text>
              <Text style={styles.settingDescription}>Automatically apply when you swipe right</Text>
            </View>
            <Switch
              value={autoApply}
              onValueChange={setAutoApply}
              trackColor={{ false: '#e0e0e0', true: '#43cea2' }}
              thumbColor={autoApply ? '#fff' : '#f4f3f4'}
            />
          </View>
        </View>

        <TouchableOpacity
          style={styles.saveButton}
          onPress={handleSaveProfile}
          disabled={saving}
        >
          {saving ? (
            <ActivityIndicator size="small" color="#fff" />
          ) : (
            <>
              <Ionicons name="checkmark-circle-outline" size={20} color="#fff" />
              <Text style={styles.saveButtonText}>Save Profile</Text>
            </>
          )}
        </TouchableOpacity>

        {error && (
          <View style={styles.errorContainer}>
            <Ionicons name="alert-circle" size={20} color="#d32f2f" />
            <Text style={styles.errorText}>{error}</Text>
          </View>
        )}

        {success && (
          <View style={styles.successContainer}>
            <Ionicons name="checkmark-circle" size={20} color="#2e7d32" />
            <Text style={styles.successText}>{success}</Text>
          </View>
        )}
      </View>

      <Modal
        visible={showResumeModal}
        transparent
        animationType="slide"
        onRequestClose={() => setShowResumeModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.resumeModalContent}>
            <Text style={styles.modalTitle}>Resume Preview</Text>
            <Text style={styles.modalFileName}>{getResumeFileName()}</Text>
            <Text style={styles.modalDescription}>
              Your resume is saved and ready for applications.
            </Text>
            <TouchableOpacity
              style={styles.modalButton}
              onPress={() => setShowResumeModal(false)}
            >
              <Text style={styles.modalButtonText}>Close</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    marginTop: 10,
    color: '#666',
    fontSize: 16,
  },
  header: {
    paddingTop: 40,
    paddingBottom: 24,
    paddingHorizontal: 16,
    borderBottomLeftRadius: 24,
    borderBottomRightRadius: 24,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1a237e',
    textAlign: 'center',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#5c6bc0',
    textAlign: 'center',
  },
  content: {
    padding: 16,
  },
  resumeBox: {
    borderRadius: 16,
    padding: 20,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
  },
  resumeHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  resumeTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 8,
    color: '#1a237e',
  },
  resumeContent: {
    alignItems: 'center',
  },
  resumeFileName: {
    fontSize: 16,
    color: '#333',
    marginBottom: 12,
    fontWeight: '500',
  },
  resumeStatus: {
    fontSize: 14,
    color: '#2e7d32',
    marginBottom: 12,
    fontWeight: '600',
  },
  resumeActions: {
    flexDirection: 'row',
    gap: 12,
  },
  resumeActionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 8,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  resumeActionText: {
    marginLeft: 4,
    color: '#333',
    fontWeight: '500',
  },
  attachResumeButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ff9800',
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 20,
    justifyContent: 'center',
  },
  attachResumeText: {
    color: '#fff',
    fontWeight: 'bold',
    marginLeft: 8,
    fontSize: 16,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1a237e',
    marginBottom: 16,
  },
  sectionDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 16,
    fontStyle: 'italic',
  },
  fieldContainer: {
    marginBottom: 16,
  },
  fieldLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  textInput: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  textArea: {
    height: 80,
    textAlignVertical: 'top',
  },
  settingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  settingInfo: {
    flex: 1,
  },
  settingLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 2,
  },
  settingDescription: {
    fontSize: 14,
    color: '#666',
  },
  saveButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#43cea2',
    borderRadius: 12,
    paddingVertical: 16,
    paddingHorizontal: 24,
    justifyContent: 'center',
    marginTop: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  saveButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 18,
    marginLeft: 8,
  },
  errorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ffebee',
    padding: 16,
    borderRadius: 12,
    marginTop: 16,
    borderWidth: 1,
    borderColor: '#ef5350',
  },
  errorText: {
    color: '#d32f2f',
    fontSize: 14,
    marginLeft: 8,
    flex: 1,
  },
  successContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#e8f5e9',
    padding: 16,
    borderRadius: 12,
    marginTop: 16,
    borderWidth: 1,
    borderColor: '#4caf50',
  },
  successText: {
    color: '#2e7d32',
    fontSize: 14,
    marginLeft: 8,
    flex: 1,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  resumeModalContent: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 24,
    width: '80%',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 8,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1a237e',
    marginBottom: 12,
  },
  modalFileName: {
    fontSize: 16,
    color: '#333',
    marginBottom: 8,
    fontWeight: '500',
  },
  modalDescription: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginBottom: 20,
  },
  modalButton: {
    backgroundColor: '#1e88e5',
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 24,
  },
  modalButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
});

export default ProfileScreen;