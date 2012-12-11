FMQ (Client-Side)
=================

What is FMQ?
------------

FMQ is a service that allows simulations of FMUs to be queued up and
run "in the cloud".  The complexity of queueing and load-balancing
simulation jobs is completely handled behind the scenes.

What is `pyfmq`?
----------------

The `pyfmq` is a small Python package that provides a Python
"front-end" to the FMQ web services API.  It allows normal Python data
to be passed in and returns a "promise" for the simulation results
that can retrieve simulation results and convert them into normal
Python data.

Installation
------------

The really easy way to install this package (for now) is to just install
the latest version on GitHub.  You can do this directly with `pip` using
the following command:

    % pip install git+git://github.com/xogeny/pyfmq.git

Usage
-----

The following example assumes that the current directory contains an
FMU whose file name is `bouncingBall.fmu`.

    import pyfmq
  
    pyfmq.setKeys("<your public key>", "<your private key>")  
  
    # This registers the FMU file with the FMQ service
    fmu = pyfmq.register("./bouncingBall.fmu")
    
    results = []
    for i in range(1,10):
      promise = pyfmq.sim(fmu, sim_args={"final_time": 10.0},
                          params={"e": 0.5+0.02*i},
                          signals=["h", "v"])
      results.append(promise)
  
    for r in results:
      print r.get()

The `params` keyword argument to the `sim` method includes a
dictionary of parameter names (as keys) which map to parameter values.
The `signals` keyword argument includes the names of all signals whose
trajectory you would like to retrieve.

Note: the current implementation requires you to specify all results
you are interested in *a priori*.  You cannot later request additional
signals.  The hope is that this limitation will be addressed in a
future release.

Promises
--------

The careful reader will not that each simulation **does not** result a
simulation result.  Instead, it returns a "promise" for a simulation
result.  The results of the simulation can be extracted using the
`get` method on the promise object.  **But note**, this will cause the
Python thread to block (wait for a result).

The example above shows a useful pattern where all jobs are submitted
first and then the results are queried.  This allows all the
simulation jobs to run in parallel and gives the biggest potential
performance.

A good "promise" implementation (and this isn't one :-), would allow
you to compose other computations together into other promise objects
(ala Akka in Scala).  I haven't gone to that extent with this library.
