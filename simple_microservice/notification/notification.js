import amqp from 'amqplib/callback_api.js';
import { transporter } from './send_email.js';
import emailTemplates from './templates.js';

// Connect to RabbitMQ using the URL from environment variables
amqp.connect(process.env.RABBIT_URL, function(error0, connection) {
  if (error0) {
    throw error0;
  }
  console.log('Connection to RabbitMQ Successful');

  // Create a channel
  connection.createChannel(function(error1, channel) {
    if (error1) {
      throw error1;
    }
    console.log('Channel created...');
    
    var exchange = 'email';

    // Assert exchange for topic-based routing
    channel.assertExchange(exchange, 'topic', { durable: true });
    console.log('Exchange asserted...');

    // Assert Queue for request related transition
    channel.assertQueue('request', { exclusive: false }, function(error2, q) {
      if (error2) {
        throw error2;
      }
      console.log(`Queue ${q.queue} created`);

      // Bind queue to listen for specific transitions like request approved/rejected
      channel.bindQueue(q.queue, exchange, "request.*");
      console.log(`Queue ${q.queue} binded to request.*...`);

      // Consume messages related to transitions between request statuses
      channel.consume(q.queue, async function(msg) {
        if (msg.fields.routingKey != "request.done") {
          console.log("==Received transition message==");

          let msgContent = JSON.parse(msg.content.toString());
          console.log('Transition message:', msgContent);

          // Get email template for the specific status transition
          let filledEmail = await emailTemplates[msg.fields.routingKey.replace(".", "_")](
            msgContent["employee"],
            msgContent["request"]
          );

          // Send email
          await transporter.sendMail(filledEmail);
          console.log("==Transition email sent==");
        }

      }, { noAck: true });
    });

    // // Assert Queue for completed actions (e.g., request fully processed)
    // channel.assertQueue('request_completed', { exclusive: false }, function(error2, q) {
    //   if (error2) {
    //     throw error2;
    //   }
    //   console.log(`Queue ${q.queue} created`);

    //   // Bind queue to listen for completed request actions
    //   channel.bindQueue(q.queue, exchange, "request.done");
    //   console.log(`Queue ${q.queue} binded to request.done...`);

    //   // Consume messages for fully completed requests
    //   channel.consume(q.queue, async function(msg) {
    //     console.log("==Received request completion message==");

    //     const msgContent = JSON.parse(msg.content.toString());
    //     console.log('Completion message:', msgContent);

    //     // Get email template for completed requests
    //     const filledEmail = await emailTemplates[msg.fields.routingKey.replace(".", "_")](
    //       msgContent["employee"],
    //       msgContent["request"]
    //     );

    //     // Send email notification
    //     await transporter.sendMail(filledEmail);
    //     console.log("==Completion email sent==");

    //   }, { noAck: true });
    // });
  });
});

