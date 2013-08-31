#
# Copyright 2013 - Tom Alessi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Email class for SSD

   This class handles returning configuration parameters for the SSD application

"""


from ssd.main.models import Config


class config_value:

    """
    Email and Pager helper class for SSD
    """

    def __init__(self):
        """
        Constructor

        """


    def value(self,config_name):
        """
        return the config_value
        """

        config_value = Config.objects.filter(config_name=config_name).values('config_value')[0]['config_value']
        return config_value
        

