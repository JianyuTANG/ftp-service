# Server

The server can be compiled and run on Linux platform.

### TO RUN

1. Make sure you have installed **gcc 7.4.0**(other versions may also work).

2. ```shell
   $ make
   ```

3. ```shell
   $ ./server -root YOUR_DIRECTORY -port YOUR_PORT
   ```

   **Arguments**:

   - -port n (optional) :  An ASCII string representing the TCP port number your server will bind to and listen for requestson. The default value is 21.
   - -root path (optional) : The pathname of the directory tree that will serve as the root for all requests. The default value is  “/tmp”.

### License

MIT License