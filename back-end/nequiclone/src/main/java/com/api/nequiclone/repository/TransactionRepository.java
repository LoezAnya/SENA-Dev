package com.api.nequiclone.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.api.nequiclone.entity.Transaction;
@Repository
public interface TransactionRepository extends JpaRepository<Transaction, Long>    {

    List<Transaction> findByAccountId(Long accountId);

}
