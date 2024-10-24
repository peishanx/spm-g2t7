import QRCode from 'qrcode';

export default {
    request: function(user_info, request_info) {
        return{
            from: process.env.email,
            to: user_info.Email, // employee's email from your employee database
            subject: `Your request #${request_info.rid} has been submitted`, // Subject line
            html: `<h2>Dear ${user_info.Staff_FName},</h2>
                        
                    <p>Your request for ${request_info.type} WFH has been submitted.</p>
                    
                    <p>Request ID: ${request_info.rid}</p>
                    <p>Status: Pending</p>
                    
                    <p>If you have any questions, please reach out to your manager.</p>`, // HTML body
        };
    },
    request_approve: function(user_info, request_info) {
        return {
            from: process.env.email,
            to: user_info.Email, // employee's email from your employee database
            subject: `Your request #${request_info.rid} has been approved`, // Subject line
            html: `<h2>Dear ${user_info.Staff_FName},</h2>
                        
                    <p>Congratulations, your request for ${request_info.type} WFH has been approved.</p>
                    
                    <p>Request ID: ${request_info.rid}</p>
                    <p>Status: Approved</p>
                    
                    <p>If you have any questions, please reach out to your manager.</p>`, // HTML body
        };
    },

    request_reject: function(user_info, request_info) {
        return {
            from: process.env.email,
            to: user_info.Email,
            subject: `Your request #${request_info.rid} has been rejected`, // Subject line
            html: `<h2>Dear ${user_info.Staff_FName},</h2>
                        
                    <p>We regret to inform you that your request for ${request_info.type} WFH has been rejected.</p>
                    
                    <p>Request ID: ${request_info.rid}</p>
                    <p>Status: Rejected</p>
                    
                    <p>If you believe this was a mistake, please contact your manager for further assistance.</p>`, // HTML body
        };
    },

    request_withdraw: function(user_info, request_info) {
        return {
            from: process.env.email,
            to: user_info.Email,
            subject: `You have withdrawn your request #${request_info.rid}`, // Subject line
            html: `<h2>Dear ${user_info.Staff_FName},</h2>
                    
                    <p>Your request for ${request_info.type} WFH has been withdrawn</p>
                    
                    <p>Request ID: ${request_info.rid}</p>
                    <p>Status: Withdrawn</p>
                    
                    <p>If this was done by mistake, please contact your manager.</p>`, // HTML body
        };
    },

    // request_pending: function(user_info, request_info) {
    //     return {
    //         from: process.env.email,
    //         to: user_info.Email,
    //         subject: `Your request #${request_info.rid} is pending approval`, // Subject line
    //         html: `<h2>Hello, ${user_info.Staff_FName}.</h2>
                        
    //                 <p>Your request for ${request_info.type} is currently pending approval.</p>
                    
    //                 <p>Request ID: ${request_info.rid}</p>
    //                 <p>Status: Pending</p>
                    
    //                 <p>We will notify you once a decision has been made. Thank you for your patience.</p>`, // HTML body
    //     };
    // },

    // request_approved_with_qr: async function(user_info, request_info, ticket_info) {
    //     let url = await QRCode.toDataURL(ticket_info.tid); // Generate QR code

    //     return {
    //         from: process.env.email,
    //         to: user_info.Email,
    //         subject: `Request #${request_info.rid} Approved: Here’s your QR Code`, // Subject line
    //         html: `<h2>Congratulations ${user_info.Staff_FName}, your request has been approved!</h2>
                        
    //                 <p>Your request for ${request_info.type} on ${request_info.date} has been approved.</p>
    //                 <p>Please present the QR code below at the relevant department:</p>

    //                 <p>
    //                     <img src="cid:${ticket_info.tid}"/>
    //                 </p>
                    
    //                 <p>Request ID: ${request_info.rid}</p>
    //                 <p>Status: Approved</p>`, // HTML body

    //         attachments: [
    //             {
    //                 filename: `${ticket_info.tid}.jpg`,
    //                 content: url.split("base64,")[1], // QR code as an image
    //                 encoding: 'base64',
    //                 cid: ticket_info.tid // Attach the QR code
    //             }
    //         ]
    //     };
    // },
};
