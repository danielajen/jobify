import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Modal,
  TextInput,
  Button,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert
} from 'react-native';
import { useUser } from '../context/UserContext';
import { API_URL } from '../config';
import * as DocumentPicker from 'expo-document-picker';
import * as FileSystem from 'expo-file-system';

const AutoApplyModal = ({ job, onClose, navigation }) => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    resume: '',
    graduation_year: '',
    degree: '',
    answers: {}
  });
  const [applicationError, setApplicationError] = useState(null);
  const [resolvingError, setResolvingError] = useState(false);
  const { user, updateUser } = useUser();
  const scrollRef = useRef();

  useEffect(() => {
    // Pre-fill form with user data
    if (user) {
      setFormData({
        name: user.name || '',
        email: user.email || '',
        phone: user.phone || '',
        resume: user.resume || '',
        graduation_year: user.graduation_year || '',
        degree: user.degree || '',
        answers: user.answers ? { ...user.answers } : {}
      });
    }

    // Fetch application errors for this job
    const fetchErrors = async () => {
      if (!job || !user) return;

      try {
        // FIXED: Remove double /api/ prefix
        const response = await fetch(`${API_URL}/application-errors?job_id=${job.id}&user_id=${user.id}`);

        if (response.ok) {
          const errors = await response.json();
          if (errors.length > 0) {
            setApplicationError(errors[0]); // Show first error
          }
        }
      } catch (error) {
        console.error('Error fetching application errors:', error);
      }
    };

    fetchErrors();
  }, [job, user]);

  const handleSubmit = async () => {
    if (!job || !user) return;

    setLoading(true);
    try {
      // FIXED: Remove double /api/ prefix
      const response = await fetch(`${API_URL}/apply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_id: job.id,
          user_info: formData
        })
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status} status`);
      }

      const result = await response.json();
      setStatus(result);

      // Clear any previous errors if successful
      setApplicationError(null);
    } catch (error) {
      console.error('Application error:', error);
      setStatus({
        status: 'error',
        message: error.message || 'Failed to submit application'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleResubmit = async (fieldName, value) => {
    try {
      // Update the form data with the corrected value
      const updatedFormData = { ...formData };

      // Update specific field
      if (fieldName in updatedFormData) {
        updatedFormData[fieldName] = value;
      } else if (fieldName in updatedFormData.answers) {
        updatedFormData.answers[fieldName] = value;
      } else {
        // Add to answers if not found
        updatedFormData.answers[fieldName] = value;
      }

      setFormData(updatedFormData);
      setResolvingError(true);



      // Wait for state update then submit
      setTimeout(() => {
        handleSubmit();
        setApplicationError(null);
        setResolvingError(false);
      }, 100);
    } catch (error) {
      console.error('Error resubmitting:', error);
    }
  };

  const updateField = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const updateAnswer = (question, answer) => {
    setFormData(prev => ({
      ...prev,
      answers: {
        ...prev.answers,
        [question]: answer
      }
    }));
  };

  const handleAttachResume = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
        copyToCacheDirectory: true
      });

      if (result.type === 'success') {
        // Upload to backend - FIXED: Remove double /api/ prefix
        const uploadUrl = `${API_URL}/upload-resume`;

        // Create form data
        const form = new FormData();
        form.append('resume', {
          uri: result.uri,
          name: result.name,
          type: result.mimeType
        });
        form.append('user_id', user.id);

        // Show loading indicator
        setLoading(true);

        const response = await fetch(uploadUrl, {
          method: 'POST',
          body: form,
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        if (!response.ok) {
          throw new Error(`Upload failed: ${response.status}`);
        }

        const data = await response.json();

        // Update form and user profile
        updateField('resume', data.resume_path);

        // Update user context
        await updateUser({
          ...user,
          resume: data.resume_path
        });

        Alert.alert('Success', 'Resume uploaded successfully');
      }
    } catch (err) {
      console.error('Resume upload error:', err);
      Alert.alert('Upload Error', err.message);
    } finally {
      setLoading(false);
    }
  };

  // Error Resolution Form Component
  const ErrorResolutionForm = () => {
    const [value, setValue] = useState('');


    if (!applicationError) return null;

    const getFieldLabel = () => {
      switch (applicationError.field_name) {
        case 'years_of_experience': return 'Years of Experience';
        case 'programming_languages': return 'Programming Languages';
        case 'gpa': return 'GPA';
        case 'resume': return 'Resume';
        default: return applicationError.field_name?.replace(/_/g, ' ') || 'Field';
      }
    };

    return (
      <View style={styles.errorResolutionContainer}>
        <Text style={styles.errorTitle}>Application Issue</Text>
        <Text style={styles.errorText}>
          {applicationError.error_type?.replace(/_/g, ' ') || 'Application Error'}
        </Text>

        {applicationError.field_name && applicationError.field_name !== 'workday_credentials' && (
          <>
            <Text style={styles.errorLabel}>Please provide {getFieldLabel()}:</Text>

            {applicationError.field_name === 'resume' ? (
              <Button
                title="Attach Resume"
                onPress={handleAttachResume}
              />
            ) : (
              <TextInput
                style={styles.input}
                value={value}
                onChangeText={setValue}
                placeholder={`Enter ${getFieldLabel()}`}
              />
            )}

            <Button
              title="Submit Correction"
              onPress={() => handleResubmit(applicationError.field_name, value)}
              color="#4CAF50"
            />
          </>
        )}


      </View>
    );
  };

  if (applicationError && !resolvingError) {
    return (
      <Modal visible={!!job} animationType="slide">
        <View style={styles.container}>
          <View style={styles.header}>
            <Text style={styles.title}>Resolve Application Issue</Text>
            <TouchableOpacity onPress={onClose} style={styles.closeButton}>
              <Text style={styles.closeText}>✕</Text>
            </TouchableOpacity>
          </View>

          <Text style={styles.jobTitle}>{job?.title} - {job?.company}</Text>

          <ErrorResolutionForm />
        </View>
      </Modal>
    );
  }

  return (
    <Modal visible={!!job} animationType="slide">
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>Apply to {job?.company}</Text>
          <TouchableOpacity onPress={onClose} style={styles.closeButton}>
            <Text style={styles.closeText}>✕</Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.jobTitle}>{job?.title}</Text>

        <ScrollView style={styles.form} ref={scrollRef}>
          <Text style={styles.sectionTitle}>Contact Information</Text>
          <TextInput
            style={styles.input}
            placeholder="Full Name"
            value={formData.name}
            onChangeText={text => updateField('name', text)}
          />
          <TextInput
            style={styles.input}
            placeholder="Email"
            value={formData.email}
            onChangeText={text => updateField('email', text)}
            keyboardType="email-address"
            autoCapitalize="none"
          />
          <TextInput
            style={styles.input}
            placeholder="Phone"
            value={formData.phone}
            onChangeText={text => updateField('phone', text)}
            keyboardType="phone-pad"
          />
          <TextInput
            style={styles.input}
            placeholder="Graduation Year"
            value={formData.graduation_year}
            onChangeText={text => updateField('graduation_year', text)}
          />
          <TextInput
            style={styles.input}
            placeholder="Degree"
            value={formData.degree}
            onChangeText={text => updateField('degree', text)}
          />



          <Text style={styles.sectionTitle}>Application Questions</Text>
          <TextInput
            style={[styles.input, styles.textArea]}
            placeholder="What are your strengths?"
            value={formData.answers?.strengths || ''}
            onChangeText={text => updateAnswer('strengths', text)}
            multiline
            numberOfLines={4}
          />
          <TextInput
            style={[styles.input, styles.textArea]}
            placeholder="Why do you want to work at this company?"
            value={formData.answers?.why_company || ''}
            onChangeText={text => updateAnswer('why_company', text)}
            multiline
            numberOfLines={4}
          />

          <View style={styles.resumeContainer}>
            <Text style={styles.resumeLabel}>
              {formData.resume ? 'Resume Attached: ' : 'No Resume Attached'}
            </Text>
            {formData.resume && <Text style={styles.resumeName}>{formData.resume.split('/').pop()}</Text>}
            <Button
              title={formData.resume ? "Change Resume" : "Attach Resume"}
              onPress={handleAttachResume}
              color="#4a86e8"
            />
          </View>
        </ScrollView>

        {loading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#0000ff" />
            <Text style={styles.loadingText}>Submitting application...</Text>
          </View>
        ) : status ? (
          <View style={[
            styles.statusContainer,
            status.status === 'success' ? styles.success : styles.error
          ]}>
            <Text style={styles.statusText}>{status.message}</Text>
            <Button title="Close" onPress={onClose} />
          </View>
        ) : (
          <View style={styles.buttonContainer}>
            <Button
              title="Cancel"
              onPress={onClose}
              color="#777"
            />
            <Button
              title="Submit Application"
              onPress={handleSubmit}
              color="#28a745"
            />
          </View>
        )}
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: 'white',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
    paddingBottom: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    flex: 1,
  },
  closeButton: {
    padding: 10,
  },
  closeText: {
    fontSize: 24,
    color: '#999',
  },
  jobTitle: {
    fontSize: 18,
    color: '#555',
    marginBottom: 25,
  },
  form: {
    flex: 1,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginTop: 15,
    marginBottom: 10,
    color: '#333',
  },
  note: {
    fontSize: 14,
    color: '#666',
    marginBottom: 10,
    fontStyle: 'italic',
  },
  input: {
    height: 50,
    borderColor: '#ddd',
    borderWidth: 1,
    marginBottom: 15,
    padding: 15,
    borderRadius: 8,
    fontSize: 16,
    backgroundColor: '#f9f9f9',
  },
  textArea: {
    height: 150,
    textAlignVertical: 'top',
  },
  resumeContainer: {
    marginVertical: 15,
    padding: 10,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    backgroundColor: '#f0f8ff',
  },
  resumeLabel: {
    fontSize: 16,
    marginBottom: 5,
  },
  resumeName: {
    fontSize: 14,
    color: '#666',
    marginBottom: 10,
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 20,
    paddingTop: 15,
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  loadingContainer: {
    padding: 20,
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 10,
  },
  statusContainer: {
    padding: 20,
    borderRadius: 10,
    marginTop: 20,
  },
  success: {
    backgroundColor: '#d4edda',
    borderColor: '#c3e6cb',
  },
  error: {
    backgroundColor: '#f8d7da',
    borderColor: '#f5c6cb',
  },
  statusText: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 15,
  },
  // Error resolution styles
  errorResolutionContainer: {
    padding: 20,
    backgroundColor: '#fff8e1',
    borderRadius: 10,
    marginTop: 20,
  },
  errorTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#d32f2f',
    marginBottom: 10,
  },
  errorText: {
    fontSize: 16,
    color: '#d32f2f',
    marginBottom: 15,
  },
  errorLabel: {
    fontSize: 16,
    marginBottom: 10,
    color: '#333',
  },
  cancelButton: {
    marginTop: 10,
  }
});

export default AutoApplyModal;