# A Python API for Demonstrating a Solution to VRP
## What is VRP?
VRP is known as Vehicle Routing Problem. This problem is a generalization of TSP (Traveling Salesman Problem). In a map we have various vehicles and various tasks. Each vehicle can chose many tasks and deliver goods. At the end we want to know the best possible way of orginising the vehicles so that, minimum time is spent.

Of course there are many different aspects. For exmaple in this implementation the capacity of the vehicles, the demand of tasks are all considered into account. Also, in this version of the problem the vehicles are not required to make a cycle.  
## How the Solution Works?
I used Google-ORTools to solve the model. I created a simple flask server and implemented the solver to be invoked in a POST request. There is a specification for the body of the request. The naming and the structure should be exactly the same.

```
{
    "vehicles": [
        {
            "id": 1,
            "start_index": 0,
            "capacity": [
                4
            ]
        }, ...
    ],
    "jobs": [
        {
            "id": 7,
            "location_index": 9,
            "delivery": [
                1
            ],
            "service": 382
        }, ...
    ],
    "matrix": [
        [0, 1, 2, 3],
        [0, 1, 2, 3],
        [0, 1, 2, 3],
        [0, 1, 2, 3],
    ]
}
```

Note that there are also some constrints in this format. For example, matrix should be a square matrix. There size cannot be lower than the maximum `location_index` variable given. 
## How Can I Use This API?
This API is not designed for a production grade level of use, rathter is is a small experimentation and a learning experience for me. Kind of a *challange*.


But if you want to run this program you can test is with *docker*. If you run `docker-compose up --build` it will build and start the server as a container. The default port is set to 5000. Then to test it you can use postman to sent a POST request to the `http://localhost:5000`. The body of the request should contiain the dictionary of vehicles, matrix and jobs. There is an example file in the repository if you want to test it.

Lastly, I want to add this area is still a new one for me. If you see any bugs, inefficiencies or problems with the model please don't hasitate to contact me.