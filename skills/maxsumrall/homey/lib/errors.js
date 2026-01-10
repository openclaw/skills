class CliError extends Error {
  /**
   * @param {string} code
   * @param {string} message
   * @param {object} [details]
   */
  constructor(code, message, details = undefined) {
    super(message);
    this.name = 'CliError';
    this.code = code;
    if (details !== undefined) this.details = details;
  }
}

/**
 * Convenience factory.
 * @param {string} code
 * @param {string} message
 * @param {object} [details]
 */
function cliError(code, message, details) {
  return new CliError(code, message, details);
}

module.exports = {
  CliError,
  cliError,
};
