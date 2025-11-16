package com.api.nequiclone.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import com.api.nequiclone.entity.*;
import java.util.Optional;
import com.api.nequiclone.entity.User;




@Repository
public interface AccountRepository extends JpaRepository<Account, Long> {

    Optional<Account> findByAccountNumber(String accountNumber);
    Optional<Account> findById(Long id);
    Optional<Account> findByUser(User user);
}
