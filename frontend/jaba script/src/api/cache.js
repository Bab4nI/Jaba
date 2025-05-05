/**
 * Cache utility for API requests
 * Provides localStorage based caching with expiration
 */

// Default cache expiry time in minutes
const DEFAULT_CACHE_TIME = 5;

// Cache namespace prefix to avoid conflicts
const CACHE_PREFIX = 'api_cache_';

/**
 * Get data from cache
 * @param {string} key - Cache key
 * @returns {any|null} - Cached data or null if not found
 */
const get = (key) => {
  try {
    const cachedItem = localStorage.getItem(`${CACHE_PREFIX}${key}`);
    if (!cachedItem) return null;
    
    const { data, expiry } = JSON.parse(cachedItem);
    
    // Check if cache has expired
    if (expiry < Date.now()) {
      localStorage.removeItem(`${CACHE_PREFIX}${key}`);
      return null;
    }
    
    return data;
  } catch (error) {
    console.error('Error reading from cache:', error);
    return null;
  }
};

/**
 * Set data in cache with expiry time
 * @param {string} key - Cache key
 * @param {any} data - Data to cache
 * @param {number} expiryMinutes - Cache expiry time in minutes
 */
const set = (key, data, expiryMinutes = DEFAULT_CACHE_TIME) => {
  try {
    const expiry = Date.now() + (expiryMinutes * 60 * 1000);
    localStorage.setItem(`${CACHE_PREFIX}${key}`, JSON.stringify({ data, expiry }));
  } catch (error) {
    // Handle potential quota exceeded errors
    if (error.name === 'QuotaExceededError' || error.name === 'NS_ERROR_DOM_QUOTA_REACHED') {
      // If storage is full, clear old cache entries
      clearOldEntries();
      try {
        // Try again after clearing
        const expiry = Date.now() + (expiryMinutes * 60 * 1000);
        localStorage.setItem(`${CACHE_PREFIX}${key}`, JSON.stringify({ data, expiry }));
      } catch (retryError) {
        console.error('Failed to set cache even after clearing old entries:', retryError);
      }
    } else {
      console.error('Error setting cache:', error);
    }
  }
};

/**
 * Remove item from cache
 * @param {string} key - Cache key
 */
const remove = (key) => {
  try {
    localStorage.removeItem(`${CACHE_PREFIX}${key}`);
  } catch (error) {
    console.error('Error removing from cache:', error);
  }
};

/**
 * Clear all cache entries
 */
const clear = () => {
  try {
    Object.keys(localStorage)
      .filter(key => key.startsWith(CACHE_PREFIX))
      .forEach(key => localStorage.removeItem(key));
  } catch (error) {
    console.error('Error clearing cache:', error);
  }
};

/**
 * Clear only expired or oldest cache entries
 * Used when storage quota is exceeded
 */
const clearOldEntries = () => {
  try {
    const now = Date.now();
    // Get all cache keys
    const cacheKeys = Object.keys(localStorage)
      .filter(key => key.startsWith(CACHE_PREFIX));
    
    // First try to remove expired entries
    let removedAny = false;
    for (const key of cacheKeys) {
      try {
        const item = JSON.parse(localStorage.getItem(key));
        if (item.expiry < now) {
          localStorage.removeItem(key);
          removedAny = true;
        }
      } catch (e) {
        localStorage.removeItem(key); // Remove invalid entries
        removedAny = true;
      }
    }
    
    // If no expired entries found, remove oldest entries (up to 20% of all entries)
    if (!removedAny && cacheKeys.length > 0) {
      const entries = cacheKeys.map(key => {
        try {
          return {
            key,
            data: JSON.parse(localStorage.getItem(key))
          };
        } catch (e) {
          return { key, data: { expiry: Infinity } };
        }
      });
      
      // Sort by expiry (oldest first)
      entries.sort((a, b) => a.data.expiry - b.data.expiry);
      
      // Remove oldest 20% of entries
      const removeCount = Math.max(1, Math.floor(entries.length * 0.2));
      entries.slice(0, removeCount).forEach(entry => {
        localStorage.removeItem(entry.key);
      });
    }
  } catch (error) {
    console.error('Error clearing old cache entries:', error);
  }
};

/**
 * Generate cache key from URL and params
 * @param {string} url - API endpoint URL
 * @param {Object} params - Query parameters
 * @returns {string} - Cache key
 */
const generateKey = (url, params = {}) => {
  return `${url}_${JSON.stringify(params)}`;
};

/**
 * Setup axios interceptors for automatic caching
 * @param {AxiosInstance} axiosInstance - Axios instance
 */
const setupAxiosCaching = (axiosInstance) => {
  // Request interceptor
  axiosInstance.interceptors.request.use(
    (config) => {
      // Skip if cache is disabled for this request
      if (config.skipCache || config.method?.toLowerCase() !== 'get') {
        return config;
      }
      
      // Generate cache key
      const cacheKey = generateKey(config.url, config.params);
      const cachedData = get(cacheKey);
      
      if (cachedData) {
        // Return cached data
        config.adapter = () => {
          return Promise.resolve({
            data: cachedData,
            status: 200,
            statusText: 'OK',
            headers: {},
            config,
            request: {}
          });
        };
      }
      
      return config;
    },
    (error) => Promise.reject(error)
  );
  
  // Response interceptor
  axiosInstance.interceptors.response.use(
    (response) => {
      // Skip if cache is disabled for this request
      if (response.config.skipCache || response.config.method?.toLowerCase() !== 'get') {
        return response;
      }
      
      // Generate cache key and store response
      const cacheKey = generateKey(response.config.url, response.config.params);
      set(cacheKey, response.data);
      
      return response;
    }
  );
  
  return axiosInstance;
};

export default {
  get,
  set,
  remove,
  clear,
  generateKey,
  setupAxiosCaching,
}; 