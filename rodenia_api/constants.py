class Categories:
    MUSIC = "music"
    DANCE = "dance"
    THEATRE = "theatre"
    FOOD = "food"


VALID_CATEGORY = ['music', 'dance', 'theatre', 'food']


# Email related constants
class EmailTypes:
    NEW_SIGNED_UP_EMAIL = "new_signed_up_email"
    ARTIST_APPROVAL_EMAIL = "artist_approval_emails"
    APPLY_EXPERIENCE_EMAIL = "apply_experience_email"
    BUY_EXPERIENCE_EMAIL = "buy_experience_email"
    CONTACT_EMAIL = "contact_email"


class NewSignedUpEmail:
    EMAIL_SUBJECT = "New Signed Up Artist"
    EMAIL_BODY = """
        <div style="font-family: Calibri;">
        <p>Thank you for creating your portfolio on Rodenia!<br /> <br />Please give us some time to review your information and links provided, we will get back to you in a few hours.<br /> <br />Here is what happens once you&rsquo;re approved on our platform:</p>
        <ol>
        <li>You can browse through all the music concert themes we have created at different venues. You can pick and choose whichever you like based on your talents and have the full autonomy to curate your own list of music you&rsquo;d like to play for the audience.</li>
        <li>You&rsquo;ll be given all the information about the experience that you&rsquo;ve applied to and we will be constantly in touch with you.</li>
        <li>We want to make sure you get fairly paid and hence after venue costs and a 20% commission of the bookings for the experience, we will transfer the rest of the amount to you (we will take your bank information to do so).</li>
        </ol>
        <br />Meanwhile, sit tight and share www.rodenia.com with your fellow musicians and music lovers!<br /> <br />Cheers!<br />Rodenia Team</div>
        """
    PLAIN_EMAIL_BODY = """
        Thank you for creating your portfolio on Rodenia!
 
        Please give us some time to review your information and links provided, we will get back to you in a few hours.
         
        Here is what happens once you’re approved on our platform:
         
        
        1. You can browse through all the music concert themes we have created at different venues. You can pick and choose whichever you like based on your talents and have the full autonomy to curate your own list of music you’d like to play for the audience.
        2. You’ll be given all the information about the experience that you’ve applied to and we will be constantly in touch with you.
        3. We want to make sure you get fairly paid and hence after venue costs and a 20% commission of the bookings for the experience, we will transfer the rest of the amount to you (we will take your bank information to do so).
         
        Meanwhile, sit tight and share www.rodenia.com with your fellow musicians and music lovers!
         
        Cheers!
        Rodenia Team
    """


class ArtistApprovalEmail:
    EMAIL_SUBJECT = "Your Registration Approval"
    APPROVED_EMAIL_BODY = """
        <div style="font-family: Calibri;">
        <p>Congrats! We reviewed your information and loved it. Your portfolio is now accessible <a href="www.rodenia.com/">here</a>.</p>
        <p>Now what?</p>
        <ul>
        <li>You can browse through all the music concert themes we have created at different venues. You can pick and choose whichever you like based on your talents.</li>
        <li>You have the full autonomy to curate your own list of music you&rsquo;d like to play for the audience within the genre/theme of experience we&rsquo;ve created on the website.<br /><br /></li>
        </ul>
        <p>If you don&rsquo;t find anything you in the options for performing or if you don&rsquo;t find your genre, don&rsquo;t worry. We are always just an email away, you can contact us anytime and we will sit with you and create an experience based on your talents and specialties for the audience at one of the incredible venues.<br /> <br />Thank you again!<br /> <br />Cheers,<br />Rodenia Team</p>
        </div>
        """
    PLAIN_APPROVED_EMAIL_BODY = """
        Congrats! We reviewed your information and loved it. Your portfolio is now accessible at www.rodenia.com.

        Now what?
        
        - You can browse through all the music concert themes we have created at different venues. You can pick and choose whichever you like based on your talents.
        - You have the full autonomy to curate your own list of music you’d like to play for the audience within the genre/theme of experience we’ve created on the website.
        
        If you don’t find anything you in the options for performing or if you don’t find your genre, don’t worry. We are always just an email away, you can contact us anytime and we will sit with you and create an experience based on your talents and specialties for the audience at one of the incredible venues.
         
        Thank you again!
         
        Cheers,
        Rodenia Team
    """
    REJECTED_EMAIL_BODY = """
        <div style="font-family: Calibri;">
        <p>Hi {name},</p>
        <p>We are extremely sorry but we couldn't accept your portfolio right now. There is usually just one reason for this - we don't have enough videos/music of you to accept. We usually like to see more content to review on and you might be a little too early to be a part of Rodenia. But don't worry! Send us an email on contact@rodenia.com and we can see more of your work and understand you better.</p>
        <p>Our mission is to bring incredible talent to the public through music and we know you are one talented musician!</p>
        <p>Hope to hear back soon!</p>
        <p>Thank you</p>
        <p>Rodenia Team</p>
        </div>
    """
    PLAIN_REJECTED_EMAIL_BODY = """
        Hi {name},

        We are extremely sorry but we couldn't accept your portfolio right now. There is usually just one reason for this - we don't have enough videos/music of you to accept. We usually like to see more content to review on and you might be a little too early to be a part of Rodenia. But don't worry! Send us an email on contact@rodenia.com and we can see more of your work and understand you better. 
        
        Our mission is to bring incredible talent to the public through music and we know you are one talented musician!
        
        Hope to hear back soon!
        
        Thank you
        
        Rodenia Team
    """


class ApplyExperienceEmail:
    EMAIL_SUBJECT = "A new artist applied to your experience!"
    EMAIL_BODY = """
        <p style="font-family: Calibri;">{artist_name} has applied for {experience_name}</p>
        """
    PLAIN_EMAIL_BODY = """
        {artist_name} has applied for {experience_name}
    """


class BuyExperienceEmail:
    EMAIL_SUBJECT = "Get Ready for your Rodenia Experience!"
    EMAIL_BODY = """
        <div style="font-family: Calibri;">
        <p>Boom! You&rsquo;re good to go!<br /> <br />Please show this when you arrive at the entrance.<br /> <br />Name &ndash; {experience_name}<br />No. of Spots &ndash; {slot}<br /> <br />Address &ndash; {address}<br /> <br /> <br />Please be on time! And if it&rsquo;s a venue which needs someone to let you in, please text us on 510-499-6974<br /> <br />Thank you! We&rsquo;re excited to see you!</p>
        </div>
    """
    PLAIN_EMAIL_BODY = """
        Boom! You’re good to go!
 
        Please show this when you arrive at the entrance.
         
        Name – {experience_name}
        No. of Spots – {slot}
         
        Address – {address}
         
         
        Please be on time! And if it’s a venue which needs someone to let you in, please text us on 510-499-6974
         
        Thank you! We’re excited to see you!
    """
