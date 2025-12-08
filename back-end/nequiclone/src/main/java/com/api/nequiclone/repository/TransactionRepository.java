package com.api.nequiclone.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

import com.api.nequiclone.entity.Transaction;

public interface TransactionRepository extends JpaRepository<Transaction, Long>    {

    List<Transaction> findByAccountId(Long accountId);

}
