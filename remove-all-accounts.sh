#!/bin/bash
for account in admin dev hprod
do
   echo "Account en cours $account"
   sls remove --aws-profile $account
done
