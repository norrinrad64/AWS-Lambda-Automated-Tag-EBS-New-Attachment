#!/bin/bash
for account in admin dev hprod
do
   sls deploy --aws-profile $account
done

