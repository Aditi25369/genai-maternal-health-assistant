/**
 * AMMA AI - Firebase Configuration
 * This file initializes Firebase for authentication and data storage
 */

// Firebase configuration - Replace with your project's config
const firebaseConfig = {
    apiKey: "your-api-key",
    authDomain: "your-project.firebaseapp.com",
    projectId: "your-project-id",
    storageBucket: "your-project.appspot.com",
    messagingSenderId: "your-sender-id",
    appId: "your-app-id"
};

// Initialize Firebase when the SDK is available
let auth = null;
let db = null;
let currentUser = null;

// Check if Firebase is available and initialize
document.addEventListener('DOMContentLoaded', function() {
    initializeFirebase();
});

function initializeFirebase() {
    // Check if Firebase SDK is loaded
    if (typeof firebase !== 'undefined') {
        try {
            // Initialize Firebase
            firebase.initializeApp(firebaseConfig);
            
            // Get Auth and Firestore instances
            auth = firebase.auth();
            db = firebase.firestore();
            
            console.log('Firebase initialized successfully');
            
            // Set up auth state listener
            auth.onAuthStateChanged((user) => {
                currentUser = user;
                if (user) {
                    console.log('User signed in:', user.uid);
                    // Store user ID in localStorage for easy access
                    localStorage.setItem('amma_ai_user_id', user.uid);
                } else {
                    console.log('No user signed in');
                    localStorage.removeItem('amma_ai_user_id');
                }
            });
            
        } catch (error) {
            console.error('Firebase initialization error:', error);
        }
    } else {
        console.log('Firebase SDK not loaded - using demo mode');
        // Set a demo user ID for development
        localStorage.setItem('amma_ai_user_id', 'demo-user-001');
    }
}

/**
 * Get current user ID
 * @returns {string} User ID or demo ID
 */
function getCurrentUserId() {
    // Return current user ID from Firebase or localStorage
    if (currentUser) {
        return currentUser.uid;
    }
    
    // Check localStorage
    const storedId = localStorage.getItem('amma_ai_user_id');
    if (storedId) {
        return storedId;
    }
    
    // Generate and store a demo ID
    const demoId = 'user-' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('amma_ai_user_id', demoId);
    return demoId;
}

/**
 * Sign in with email and password
 * @param {string} email 
 * @param {string} password 
 * @returns {Promise}
 */
async function signInWithEmail(email, password) {
    if (!auth) {
        throw new Error('Firebase Auth not initialized');
    }
    
    try {
        const result = await auth.signInWithEmailAndPassword(email, password);
        return result.user;
    } catch (error) {
        console.error('Sign in error:', error);
        throw error;
    }
}

/**
 * Sign up with email and password
 * @param {string} email 
 * @param {string} password 
 * @returns {Promise}
 */
async function signUpWithEmail(email, password) {
    if (!auth) {
        throw new Error('Firebase Auth not initialized');
    }
    
    try {
        const result = await auth.createUserWithEmailAndPassword(email, password);
        return result.user;
    } catch (error) {
        console.error('Sign up error:', error);
        throw error;
    }
}

/**
 * Sign in anonymously (for quick access)
 * @returns {Promise}
 */
async function signInAnonymously() {
    if (!auth) {
        throw new Error('Firebase Auth not initialized');
    }
    
    try {
        const result = await auth.signInAnonymously();
        return result.user;
    } catch (error) {
        console.error('Anonymous sign in error:', error);
        throw error;
    }
}

/**
 * Sign out
 * @returns {Promise}
 */
async function signOut() {
    if (!auth) {
        return;
    }
    
    try {
        await auth.signOut();
        localStorage.removeItem('amma_ai_user_id');
        currentUser = null;
    } catch (error) {
        console.error('Sign out error:', error);
        throw error;
    }
}

/**
 * Get user profile from Firestore
 * @returns {Promise<Object|null>}
 */
async function getUserProfile() {
    const userId = getCurrentUserId();
    
    // Try to get from localStorage first (for offline/cached access)
    const cached = localStorage.getItem('user_profile_' + userId);
    if (cached) {
        return JSON.parse(cached);
    }
    
    // If Firebase is available, fetch from Firestore
    if (db) {
        try {
            const doc = await db.collection('users').doc(userId).get();
            if (doc.exists) {
                const profile = doc.data();
                // Cache locally
                localStorage.setItem('user_profile_' + userId, JSON.stringify(profile));
                return profile;
            }
        } catch (error) {
            console.error('Error fetching profile:', error);
        }
    }
    
    return null;
}

/**
 * Save user profile to Firestore and localStorage
 * @param {Object} profile 
 * @returns {Promise<boolean>}
 */
async function saveUserProfile(profile) {
    const userId = getCurrentUserId();
    
    // Always save to localStorage
    localStorage.setItem('user_profile_' + userId, JSON.stringify(profile));
    
    // If Firebase is available, save to Firestore
    if (db) {
        try {
            await db.collection('users').doc(userId).set(profile, { merge: true });
            return true;
        } catch (error) {
            console.error('Error saving profile:', error);
            return false;
        }
    }
    
    return true;
}

/**
 * Save chat message to Firestore
 * @param {Object} messageData 
 * @returns {Promise<boolean>}
 */
async function saveChatMessage(messageData) {
    if (!db) {
        // Store in localStorage as fallback
        const messages = JSON.parse(localStorage.getItem('chat_messages') || '[]');
        messages.push({
            ...messageData,
            timestamp: new Date().toISOString(),
            id: 'local-' + Date.now()
        });
        localStorage.setItem('chat_messages', JSON.stringify(messages.slice(-100))); // Keep last 100
        return true;
    }
    
    try {
        await db.collection('chat_sessions')
            .doc(messageData.session_id)
            .collection('messages')
            .add({
                ...messageData,
                timestamp: firebase.firestore.FieldValue.serverTimestamp()
            });
        return true;
    } catch (error) {
        console.error('Error saving message:', error);
        return false;
    }
}

/**
 * Get chat history from Firestore or localStorage
 * @param {string} sessionId 
 * @returns {Promise<Array>}
 */
async function getChatHistory(sessionId) {
    if (!db) {
        // Get from localStorage
        const messages = JSON.parse(localStorage.getItem('chat_messages') || '[]');
        return messages.filter(m => m.session_id === sessionId);
    }
    
    try {
        const snapshot = await db.collection('chat_sessions')
            .doc(sessionId)
            .collection('messages')
            .orderBy('timestamp', 'asc')
            .limit(50)
            .get();
        
        return snapshot.docs.map(doc => ({
            id: doc.id,
            ...doc.data()
        }));
    } catch (error) {
        console.error('Error fetching chat history:', error);
        return [];
    }
}

// Export functions for use in other modules
window.firebaseConfig = {
    getCurrentUserId,
    getUserProfile,
    saveUserProfile,
    saveChatMessage,
    getChatHistory,
    signInWithEmail,
    signUpWithEmail,
    signInAnonymously,
    signOut
};
