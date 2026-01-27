/**
 * Fliz API Node.js Client
 * 
 * A complete JavaScript/TypeScript wrapper for the Fliz REST API.
 * 
 * Installation:
 *   npm install axios
 * 
 * Usage:
 *   const FlizClient = require('./nodejs_client');
 *   const client = new FlizClient('YOUR_API_KEY');
 *   
 *   const result = await client.createVideo({
 *     name: 'My Video',
 *     description: 'Full article content...',
 *     format: 'size_16_9',
 *     lang: 'en'
 *   });
 */

const axios = require('axios');

class FlizAPIError extends Error {
  constructor(message, statusCode = null, response = null) {
    super(message);
    this.name = 'FlizAPIError';
    this.statusCode = statusCode;
    this.response = response;
  }
}

class FlizClient {
  static BASE_URL = 'https://app.fliz.ai';
  
  // Terminal states
  static COMPLETE_STATES = new Set(['complete']);
  static ERROR_STATES = new Set(['failed', 'failed_unrecoverable', 'failed_go_back_to_user_action']);
  static BLOCKED_STATES = new Set(['user_action', 'block']);

  /**
   * Create a new Fliz client
   * @param {string} apiKey - Your Fliz API key from https://app.fliz.ai/api-keys
   * @param {object} options - Optional configuration
   * @param {string} options.baseUrl - Custom base URL
   * @param {number} options.timeout - Request timeout in ms (default: 60000)
   */
  constructor(apiKey, options = {}) {
    this.apiKey = apiKey;
    this.baseUrl = options.baseUrl || FlizClient.BASE_URL;
    this.timeout = options.timeout || 60000;
    
    this.client = axios.create({
      baseURL: this.baseUrl,
      timeout: this.timeout,
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      }
    });
  }

  /**
   * Make API request with error handling
   */
  async _request(method, endpoint, data = null, params = null) {
    try {
      const response = await this.client.request({
        method,
        url: endpoint,
        data,
        params
      });
      return response.data;
    } catch (error) {
      if (error.response) {
        const status = error.response.status;
        const message = error.response.data?.error || error.response.statusText;
        
        if (status === 401) {
          throw new FlizAPIError('Invalid or expired API key', 401);
        }
        if (status === 429) {
          throw new FlizAPIError('Rate limit exceeded', 429);
        }
        throw new FlizAPIError(message, status, error.response.data);
      }
      throw new FlizAPIError(error.message);
    }
  }

  /**
   * Test API connection
   * @returns {Promise<boolean>}
   */
  async testConnection() {
    await this.getVoices();
    return true;
  }

  // ========== Video Operations ==========

  /**
   * Create a new video
   * @param {object} options - Video creation options
   * @param {string} options.name - Video title (required)
   * @param {string} options.description - Full text content (required)
   * @param {string} options.format - size_16_9, size_9_16, or square
   * @param {string} options.lang - Language ISO code
   * @param {string} options.category - article, product, or ad
   * @param {string} options.scriptStyle - Narrative style
   * @param {string} options.imageStyle - Visual style
   * @param {string[]} options.imageUrls - Image URLs (required for product/ad)
   * @param {string} options.captionStyle - Subtitle style
   * @param {string} options.captionPosition - bottom or center
   * @param {string} options.captionFont - Font family
   * @param {string} options.captionColor - Hex color
   * @param {boolean} options.captionUppercase - Uppercase captions
   * @param {string} options.voiceId - Custom voice ID
   * @param {boolean} options.isMaleVoice - Use male voice
   * @param {string} options.musicId - Background music ID
   * @param {string} options.musicUrl - Custom music URL
   * @param {number} options.musicVolume - Volume 0-100
   * @param {string} options.watermarkUrl - Watermark image URL
   * @param {string} options.siteUrl - Call-to-action URL
   * @param {string} options.siteName - Call-to-action text
   * @param {string} options.webhookUrl - Callback URL
   * @param {boolean} options.isAutomatic - Auto-process (default: true)
   * @param {string} options.videoAnimationMode - full_video or hook_only
   * @returns {Promise<{video_id: string}>}
   */
  async createVideo(options) {
    const {
      name,
      description,
      format = 'size_16_9',
      lang = 'en',
      category = 'article',
      scriptStyle,
      imageStyle,
      imageUrls,
      captionStyle,
      captionPosition,
      captionFont,
      captionColor,
      captionUppercase,
      voiceId,
      isMaleVoice,
      musicId,
      musicUrl,
      musicVolume,
      watermarkUrl,
      siteUrl,
      siteName,
      webhookUrl,
      isAutomatic = true,
      videoAnimationMode
    } = options;

    // Build params object
    const params = {
      name,
      description,
      format,
      lang,
      category,
      is_automatic: isAutomatic
    };

    // Add optional params (convert camelCase to snake_case)
    const optionalMappings = {
      scriptStyle: 'script_style',
      imageStyle: 'image_style',
      imageUrls: 'image_urls',
      captionStyle: 'caption_style',
      captionPosition: 'caption_position',
      captionFont: 'caption_font',
      captionColor: 'caption_color',
      captionUppercase: 'caption_uppercase',
      voiceId: 'voice_id',
      isMaleVoice: 'is_male_voice',
      musicId: 'music_id',
      musicUrl: 'music_url',
      musicVolume: 'music_volume',
      watermarkUrl: 'watermark_url',
      siteUrl: 'site_url',
      siteName: 'site_name',
      webhookUrl: 'webhook_url',
      videoAnimationMode: 'video_animation_mode'
    };

    for (const [camel, snake] of Object.entries(optionalMappings)) {
      if (options[camel] !== undefined) {
        params[snake] = options[camel];
      }
    }

    const response = await this._request('POST', '/api/rest/video', {
      fliz_video_create_input: params
    });

    return response.fliz_video_create;
  }

  /**
   * Get video by ID
   * @param {string} videoId - Video UUID
   * @returns {Promise<object|null>}
   */
  async getVideo(videoId) {
    const response = await this._request('GET', `/api/rest/videos/${videoId}`);
    return response.fliz_video_by_pk;
  }

  /**
   * Get simplified video status
   * @param {string} videoId - Video UUID
   * @returns {Promise<object>}
   */
  async getVideoStatus(videoId) {
    const video = await this.getVideo(videoId);
    
    if (!video) {
      throw new FlizAPIError(`Video not found: ${videoId}`);
    }

    const step = video.step || 'unknown';

    return {
      step,
      url: video.url,
      error: video.error,
      isComplete: FlizClient.COMPLETE_STATES.has(step),
      isError: FlizClient.ERROR_STATES.has(step),
      isBlocked: FlizClient.BLOCKED_STATES.has(step),
      video
    };
  }

  /**
   * List videos with pagination
   * @param {number} limit - Number of results
   * @param {number} offset - Pagination offset
   * @returns {Promise<object[]>}
   */
  async listVideos(limit = 20, offset = 0) {
    const response = await this._request('GET', '/api/rest/videos', null, {
      limit,
      offset
    });
    return response.fliz_video || [];
  }

  /**
   * Wait for video completion
   * @param {string} videoId - Video UUID
   * @param {object} options - Polling options
   * @param {number} options.pollInterval - Seconds between polls (default: 15)
   * @param {number} options.timeout - Maximum wait time in seconds (default: 600)
   * @param {function} options.onProgress - Callback called on each poll
   * @returns {Promise<object>} - Final video object
   */
  async waitForVideo(videoId, options = {}) {
    const {
      pollInterval = 15,
      timeout = 600,
      onProgress = null
    } = options;

    const startTime = Date.now();

    while (true) {
      const elapsed = (Date.now() - startTime) / 1000;

      if (elapsed > timeout) {
        throw new FlizAPIError(`Timeout after ${Math.floor(elapsed)}s`, null, { videoId });
      }

      const status = await this.getVideoStatus(videoId);

      if (onProgress) {
        onProgress(status);
      }

      if (status.isComplete) {
        return status.video;
      }

      if (status.isError) {
        throw new FlizAPIError(`Video failed: ${status.step}`, null, status.video);
      }

      if (status.isBlocked) {
        throw new FlizAPIError(`Video blocked: ${status.step}`, null, status.video);
      }

      await this._sleep(pollInterval * 1000);
    }
  }

  /**
   * Translate video to new language
   * @param {string} videoId - Source video UUID
   * @param {string} newLang - Target language ISO code
   * @param {object} options - Additional options
   * @returns {Promise<{new_video_id: string}>}
   */
  async translateVideo(videoId, newLang, options = {}) {
    const params = { new_lang: newLang };
    
    if (options.isAutomatic !== undefined) {
      params.is_automatic = options.isAutomatic;
    }
    if (options.webhookUrl) {
      params.webhook_url = options.webhookUrl;
    }

    const response = await this._request(
      'POST',
      `/api/rest/videos/${videoId}/translate`,
      null,
      params
    );
    return response.fliz_video_translate;
  }

  /**
   * Duplicate video
   * @param {string} videoId - Source video UUID
   * @returns {Promise<{new_video_id: string}>}
   */
  async duplicateVideo(videoId) {
    const response = await this._request(
      'POST',
      `/api/rest/videos/${videoId}/duplicate`
    );
    return response.fliz_video_duplicate;
  }

  // ========== Resources ==========

  /**
   * Get available voices
   * @returns {Promise<object[]>}
   */
  async getVoices() {
    const response = await this._request('GET', '/api/rest/voices');
    return response.fliz_list_voices?.voices || [];
  }

  /**
   * Get available music tracks
   * @returns {Promise<object[]>}
   */
  async getMusics() {
    const response = await this._request('GET', '/api/rest/musics');
    return response.fliz_list_musics?.musics || [];
  }

  // ========== Utilities ==========

  _sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

module.exports = FlizClient;
module.exports.FlizAPIError = FlizAPIError;


// ========== Example Usage ==========

if (require.main === module) {
  (async () => {
    const API_KEY = process.env.FLIZ_API_KEY || 'your-api-key-here';

    const client = new FlizClient(API_KEY);

    try {
      // Test connection
      await client.testConnection();
      console.log('✅ Connection successful!');

      // List voices
      const voices = await client.getVoices();
      console.log(`\n🎙️ Found ${voices.length} voices`);

      // Create video
      console.log('\n📹 Creating video...');
      const result = await client.createVideo({
        name: 'Test Video',
        description: 'This is a test video created via the Fliz API.',
        format: 'size_16_9',
        lang: 'en',
        imageStyle: 'digital_art'
      });
      console.log(`   Video ID: ${result.video_id}`);

      // Wait for completion
      console.log('\n⏳ Waiting for video...');
      const video = await client.waitForVideo(result.video_id, {
        pollInterval: 10,
        onProgress: (status) => console.log(`   Status: ${status.step}`)
      });
      console.log(`\n✅ Video ready: ${video.url}`);

    } catch (error) {
      console.error(`\n❌ Error: ${error.message}`);
      process.exit(1);
    }
  })();
}
