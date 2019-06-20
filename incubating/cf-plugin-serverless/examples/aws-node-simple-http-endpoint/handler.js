'use strict';

module.exports.endpoint = (event, context, callback) => {
  const response = {
    statusCode: 200,
    body: JSON.stringify({
      message: `Hello, 
      the current time: ${new Date().toTimeString()},
      the event: ${JSON.stringify(event)}, 
      the context: ${JSON.stringify(context)}`,
    }),
  };

  callback(null, response);
};
