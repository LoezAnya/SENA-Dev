package com.api.nequiclone.service.implementation;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import org.springframework.stereotype.Service;

import com.api.nequiclone.entity.Account;
import com.api.nequiclone.entity.User;
import com.api.nequiclone.enums.AccountStatus;
import com.api.nequiclone.service.interfaces.AccountService;

@Service
public class AccountServiceImp implements AccountService {

    @Override
    public Account createAccount(User user) {
        Account account = new Account();
        account.setUser(user);
        account.setAccountNumber(user.getPhoneNumber());
        account.setBalance(BigDecimal.ZERO);
        account.setCurrency("COP");
        account.setStatus(AccountStatus.ACTIVE);
        account.setCreatedAt(LocalDateTime.now());
        return account;
    }


    @Override
    public Account getAccountById(Long id) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'getAccountById'");
    }

    @Override
    public Account getAccountByNumber(String accountNumber) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'getAccountByNumber'");
    }

    @Override
    public Account updateAccountNumber(Account account) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'updateAccountNumber'");
    }

    @Override
    public Account updateAccountBalance(Long accountId, BigDecimal newBalance) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'updateAccountBalance'");
    }

    @Override
    public void deactivateAccount(Long accountId) {
        // TODO Auto-generated method stub
        throw new UnsupportedOperationException("Unimplemented method 'deactivateAccount'");
    }


    
}
