PRESIGN()                                                            PRESIGN()



NNAAMMEE
       presign -

DDEESSCCRRIIPPTTIIOONN
       Generate  a  pre-signed URL for an Amazon S3 object. This allows anyone
       who receives the pre-signed URL to retrieve the S3 object with an  HTTP
       GET  request.  For sigv4 requests the region needs to be configured ex-
       plicitly.

       See 'aws help' for descriptions of global parameters.

SSYYNNOOPPSSIISS
            presign
          <S3Uri>
          [--expires-in <value>]

OOPPTTIIOONNSS
       ppaatthh (string)

       ----eexxppiirreess--iinn (integer) Number of seconds until the pre-signed  URL  ex-
       pires. Default is 3600 seconds.

       See 'aws help' for descriptions of global parameters.



                                                                     PRESIGN()
