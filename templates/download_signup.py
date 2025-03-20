<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Download Credentials - Note That</title>
  <script>
    window.onload = function() {
      // Automatically trigger the download for signup credentials
      var link = document.createElement('a');
      link.href = "{{ url_for('download_signup_csv') }}";
      document.body.appendChild(link);
      link.click();
      // Redirect to login after 3 seconds
      setTimeout(function() {
        window.location.href = "{{ url_for('login') }}";
      }, 3000);
    }
  </script>
</head>
<body>
  <p>Your credentials are being downloaded. You will be redirected to the login page shortly.</p>
</body>
</html>
